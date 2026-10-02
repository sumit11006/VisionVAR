import os
import json
import time
from pathlib import Path
from typing import Optional
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.database import SessionLocal
from backend.app.models.session import AnalysisSession
from backend.app.models.video import Video
from backend.app.websocket.manager import ws_manager
from backend.cv.video_processor import VideoProcessor, VideoProcessingError
from backend.cv.detection.service import DetectionService, DetectionError
from backend.cv.tracking.tracking_service import TrackingService
from backend.cv.team.service import TeamClassificationService
from backend.cv.pitch.service import PitchMappingService
from backend.cv.formation.service import FormationService
from backend.cv.ball.service import BallTrackingService
from backend.cv.events.ball_contact import BallContactService
from backend.cv.offside.service import OffsideAnalysisService
from backend.cv.events.service import EventDetectionService
from backend.cv.events.pass_detection import PassDetectionService
from backend.cv.events.shot_detection import ShotDetectionService
from backend.cv.events.goal_detection import GoalDetectionService
from backend.cv.events.possession import PossessionService
from backend.cv.analytics.player_analytics import PlayerAnalyticsService
from backend.cv.analytics.match_summary import MatchSummaryService
from backend.app.models.event import MatchEvent

async def run_detection_pipeline(
    session_id: str,
    video_id: Optional[str] = None,
    frame_skip: Optional[int] = None,
    conf_threshold: Optional[float] = None,
):
    """
    Background worker that runs OpenCV frame extraction, YOLO inference,
    and streams real-time updates over WebSocket.
    """
    skip = frame_skip if frame_skip is not None else settings.FRAME_SKIP
    db: Session = SessionLocal()

    try:
        # 1. Fetch Session
        session = db.query(AnalysisSession).filter(AnalysisSession.id == session_id).first()
        if not session:
            return

        # 2. Resolve Video
        target_vid_id = video_id or session.video_id
        video = None
        if target_vid_id:
            video = db.query(Video).filter(Video.id == target_vid_id).first()

        if not video:
            # Fallback to most recent video in database
            video = db.query(Video).order_by(Video.created_at.desc()).first()

        if not video or not Path(video.file_path).exists():
            await ws_manager.broadcast_to_session(
                session_id,
                {
                    "type": "processing_status",
                    "session_id": session_id,
                    "status": "error",
                    "progress": 0.0,
                    "message": f"No valid video file found for session '{session_id}'.",
                },
            )
            session.status = "ERROR"
            db.commit()
            return

        # Update Session state to PROCESSING
        session.status = "PROCESSING"
        session.current_stage = "YOLO_DETECTION"
        session.progress_percent = 0
        db.commit()

        # 3. Initialize VideoProcessor & DetectionService & TrackingService
        detector = DetectionService(confidence_threshold=conf_threshold)
        tracker = TrackingService()
        ball_tracker = BallTrackingService()
        team_classifier = TeamClassificationService()
        pitch_mapper = PitchMappingService()
        formation_analyzer = FormationService()
        ball_contact_analyzer = BallContactService()
        offside_analyzer = OffsideAnalysisService()
        event_detector = EventDetectionService()
        pass_detector = PassDetectionService()
        shot_detector = ShotDetectionService()
        goal_detector = GoalDetectionService()
        possession_tracker = PossessionService(distance_threshold_m=2.5, firm_possession_frames=5)
        with VideoProcessor(video.file_path) as vp:
            total_frames = vp.total_frames
            fps = vp.fps
            
            # Phase 7F: Player Analytics
            player_analytics = PlayerAnalyticsService(fps=fps)

            # Update video metadata if not populated
            if not video.fps or video.fps <= 0 or not video.total_frames:
                video.fps = fps
                video.total_frames = total_frames
                video.duration_seconds = vp.duration_seconds
                video.resolution = f"{vp.width}x{vp.height}"
                db.commit()

            # Broadcast initial started status
            await ws_manager.broadcast_to_session(
                session_id,
                {
                    "type": "processing_status",
                    "session_id": session_id,
                    "status": "processing",
                    "progress": 0.0,
                    "current_frame": 0,
                    "total_frames": total_frames,
                    "fps": fps,
                    "duration_seconds": vp.duration_seconds,
                    "resolution": f"{vp.width}x{vp.height}",
                    "width": vp.width,
                    "height": vp.height,
                    "message": f"Starting YOLO detection on {vp.video_path.name} ({total_frames} frames)...",
                },
            )

            detection_records = []
            tracking_records = []
            processed_count = 0
            start_time = time.time()

            # 4. Process frames sequentially
            import asyncio
            for frame_idx, timestamp, frame_bgr in vp.iter_frames(frame_skip=skip):
                t0 = time.time()
                frame_result = await asyncio.to_thread(
                    detector.detect_frame,
                    frame_bgr,
                    frame_number=frame_idx,
                    timestamp=timestamp,
                    conf_threshold=conf_threshold,
                )
                inference_ms = round((time.time() - t0) * 1000, 1)

                processed_count += 1
                progress = round(min(99.0, (frame_idx / max(1, total_frames)) * 100.0), 1)

                # Record frame data for metadata artifact
                detection_records.append({
                    "frame": frame_idx,
                    "timestamp": timestamp,
                    "inference_ms": inference_ms,
                    "player_count": len([d for d in frame_result.detections if d.class_name == "player"]),
                    "ball_detected": any(d.class_name == "ball" for d in frame_result.detections),
                    "detections": [d.model_dump(by_alias=True) for d in frame_result.detections],
                })
                
                # Tracking
                t1 = time.time()
                player_detections = [d for d in frame_result.detections if d.class_name == "player"]
                ball_detections = [d for d in frame_result.detections if d.class_name == "ball"]
                
                tracked_items = tracker.update(player_detections, frame_idx, timestamp)
                ball_state = ball_tracker.update(ball_detections, frame_idx, timestamp)
                
                # Team Classification
                tracked_items = team_classifier.process_tracked_items(tracked_items, frame_bgr)
                
                # Pitch Mapping
                pitch_status = pitch_mapper.calibrate(frame_bgr)
                if pitch_status == "mapped":
                    for item in tracked_items:
                        if item.class_name == "player":
                            # BBox is pydantic object, pass as dict or object
                            pitch_pos = pitch_mapper.project_player(item.bbox.model_dump())
                            if pitch_pos:
                                item.pitch_position = pitch_pos
                                item.mapping_status = "mapped"
                            else:
                                item.mapping_status = "out_of_bounds"
                                
                    # Map the ball
                    if ball_state and ball_state.get("bbox"):
                        # Format bbox for project_player
                        ball_bbox_dict = {
                            "x1": ball_state["bbox"][0],
                            "y1": ball_state["bbox"][1],
                            "x2": ball_state["bbox"][2],
                            "y2": ball_state["bbox"][3]
                        }
                        ball_pitch_pos = pitch_mapper.project_player(ball_bbox_dict)
                        if ball_pitch_pos:
                            ball_state = ball_tracker.update_pitch_position(ball_state, (ball_pitch_pos["x"], ball_pitch_pos["y"]))
                            
                    if ball_state:
                        ball_state["movement_trail"] = ball_tracker.get_trajectory()
                else:
                    for item in tracked_items:
                        item.mapping_status = pitch_status
                        
                # Formation Analysis
                formation_result = formation_analyzer.process_frame(tracked_items)
                
                # Phase 6B: Events and Offside Candidate Analysis
                ball_contact_event = ball_contact_analyzer.process_frame(ball_state, frame_idx, timestamp)
                
                offside_candidate = None
                if ball_contact_event.get("state") == "possible":
                    offside_candidate = offside_analyzer.analyze(
                        ball_contact=ball_contact_event,
                        tracked_items=tracked_items,
                        timestamp=timestamp,
                        frame=frame_idx
                    )
                
                tracking_ms = round((time.time() - t1) * 1000, 1)

                # Stream frame detection over WebSocket
                # Need to add movement_trail safely since it's a dynamic attribute
                dumped_items = []
                for t in tracked_items:
                    d = t.model_dump(by_alias=True)
                    if hasattr(t, 'movement_trail'):
                        d['movement_trail'] = t.movement_trail
                    dumped_items.append(d)

                payload = {
                    "type": "frame_tracking",
                    "session_id": session_id,
                    "frame": frame_idx,
                    "total_frames": total_frames,
                    "fps": fps,
                    "duration_seconds": vp.duration_seconds,
                    "width": vp.width,
                    "height": vp.height,
                    "timestamp": timestamp,
                    "inference_time_ms": inference_ms,
                    "tracking_time_ms": tracking_ms,
                    "tracked_items": dumped_items,
                    "formation": formation_result,
                    "ball": ball_state
                }
                
                if offside_candidate:
                    payload["offside"] = offside_candidate

                tracking_records.append({
                    "frame_number": frame_idx,
                    "timestamp": timestamp,
                    "tracked_items": dumped_items,
                    "ball_state": ball_state,
                    "formation": formation_result,
                    "pitch_mapping_status": pitch_status
                })

                await ws_manager.broadcast_to_session(session_id, payload)
                
                # Phase 7A: Event Generation
                detected_events = event_detector.process(
                    frame_idx=frame_idx,
                    timestamp=timestamp,
                    session_id=session_id,
                    match_id=session.match_id,
                    tracked_items=tracked_items,
                    ball_state=ball_state,
                    ball_contact_event=ball_contact_event,
                    offside_candidate=offside_candidate
                )
                
                # Phase 7B: Pass Detection
                pass_events = pass_detector.process(
                    frame_idx=frame_idx,
                    timestamp=timestamp,
                    session_id=session_id,
                    match_id=session.match_id,
                    tracked_items=tracked_items,
                    ball_state=ball_state,
                    ball_contact_event=ball_contact_event
                )
                detected_events.extend(pass_events)
                
                # Phase 7C: Shot Detection
                shot_events = shot_detector.process(
                    frame_idx=frame_idx,
                    timestamp=timestamp,
                    session_id=session_id,
                    match_id=session.match_id,
                    tracked_items=tracked_items,
                    ball_state=ball_state,
                    ball_contact_event=ball_contact_event
                )
                
                # Phase 7D: Goal Detection
                attacking_directions = {
                    "team_a": shot_detector.determine_attacking_direction("team_a", tracked_items),
                    "team_b": shot_detector.determine_attacking_direction("team_b", tracked_items)
                }
                
                goal_events = goal_detector.process(
                    frame_idx=frame_idx,
                    timestamp=timestamp,
                    session_id=session_id,
                    match_id=session.match_id,
                    ball_state=ball_state,
                    attacking_directions=attacking_directions,
                    active_shots=[shot_detector.active_shot] if shot_detector.active_shot else None
                )
                
                # Shot/Pass separation logic
                # If both a pass and shot are detected simultaneously (or within 1s), resolve ambiguity.
                # Actually, PASS triggers on reception. SHOT triggers mid-flight (distance >= min_shot_distance).
                # To prevent SHOT from masking PASS, we can just let them co-exist if they are fundamentally different events,
                # but if they happen on the exact same frame, we can resolve.
                # Usually they happen on different frames because Pass detects at reception, Shot detects in transit.
                detected_events.extend(shot_events)
                detected_events.extend(goal_events)
                
                # Phase 7E & 7E.1: Possession & Turnover Detection
                possession_events = possession_tracker.process(
                    frame_idx=frame_idx,
                    timestamp=timestamp,
                    tracked_items=tracked_items,
                    ball_state=ball_state,
                    ball_contact_event=ball_contact_event
                )
                
                # Add basic IDs to possession events for db insertion
                import uuid
                for pe in possession_events:
                    pe["id"] = f"evt_pos_{uuid.uuid4().hex[:8]}"
                    pe["match_id"] = session.match_id
                    
                # Phase 7F: Player Analytics accumulation
                player_analytics.process_frame(
                    frame_idx=frame_idx,
                    timestamp=timestamp,
                    tracked_items=tracked_items,
                    events=detected_events + possession_events
                )
                
                detected_events.extend(possession_events)
                
                for ev in detected_events:
                    # Save to DB
                    db_event = MatchEvent(
                        id=ev["id"],
                        match_id=ev["match_id"],
                        minute=int(ev["timestamp"] // 60),
                        second=int(ev["timestamp"] % 60),
                        frame_id=ev["frame"],
                        type=ev["event_type"],
                        team=ev["team"],
                        player=ev["player"],
                        status=ev["status"],
                        confidence=ev["confidence"],
                        metadata_json=json.dumps(ev["metadata"]) if ev.get("metadata") else None
                    )
                    db.add(db_event)
                    
                    # Broadcast event over WebSocket
                    await ws_manager.broadcast_to_session(
                        session_id,
                        {
                            "type": "event_detected",
                            "session_id": session_id,
                            "event": ev
                        }
                    )
                
                db.commit()

                # Periodic status update every 5 processed frames
                if processed_count % 5 == 0:
                    session.progress_percent = int(progress)
                    db.commit()
                    await ws_manager.broadcast_to_session(
                        session_id,
                        {
                            "type": "processing_status",
                            "session_id": session_id,
                            "status": "processing",
                            "progress": progress,
                            "current_frame": frame_idx,
                            "total_frames": total_frames,
                            "fps": fps,
                            "duration_seconds": vp.duration_seconds,
                            "width": vp.width,
                            "height": vp.height,
                        },
                    )

                # Yield control to event loop for immediate WebSocket frame delivery
                await asyncio.sleep(0.005)

            # 5. Save detection metadata artifact to disk
            sessions_dir = Path(settings.SESSIONS_DIR) / session_id
            sessions_dir.mkdir(parents=True, exist_ok=True)
            artifact_file = sessions_dir / "detections.json"

            summary = {
                "session_id": session_id,
                "video_id": video.id,
                "video_file": video.filename,
                "total_frames": total_frames,
                "processed_frames": processed_count,
                "frame_skip": skip,
                "fps": fps,
                "processing_duration_seconds": round(time.time() - start_time, 2),
                "total_detections_count": sum(len(r["detections"]) for r in detection_records),
                "records": detection_records,
            }

            with open(artifact_file, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2)
                
            tracking_results_file = sessions_dir / "tracking_results.json"
            with open(tracking_results_file, "w", encoding="utf-8") as f:
                json.dump({"session_id": session_id, "frames": tracking_records}, f)
                
            # Phase 7F: Save player analytics artifact
            analytics_summary = player_analytics.get_summary()
            analytics_summary["match_id"] = session.match_id
            analytics_summary["session_id"] = session_id
            analytics_file = sessions_dir / "analytics.json"
            with open(analytics_file, "w", encoding="utf-8") as f:
                json.dump(analytics_summary, f, indent=2)

            # Phase 7G: Generate Match Summary
            summary_service = MatchSummaryService()
            db_events = db.query(MatchEvent).filter(MatchEvent.match_id == session.match_id).all()
            events_dict_list = []
            for ev in db_events:
                events_dict_list.append({
                    "id": ev.id,
                    "event_type": ev.type,
                    "player": ev.player,
                    "metadata": json.loads(ev.metadata_json) if ev.metadata_json else {"state": ev.status}
                })
                
            video_meta = {
                "total_frames": total_frames,
                "duration_seconds": vp.duration_seconds
            }
            
            match_summary = summary_service.generate_summary(
                session_id=session_id,
                events=events_dict_list,
                analytics_data=analytics_summary,
                detections_meta=summary,
                video_meta=video_meta
            )
            
            match_summary_file = sessions_dir / "match_summary.json"
            with open(match_summary_file, "w", encoding="utf-8") as f:
                json.dump(match_summary, f, indent=2)

            # 6. Mark Session Completed
            session.status = "READY"
            session.progress_percent = 100
            session.current_stage = "DETECTION_COMPLETE"
            db.commit()

            # Broadcast completed status
            await ws_manager.broadcast_to_session(
                session_id,
                {
                    "type": "processing_status",
                    "session_id": session_id,
                    "status": "completed",
                    "progress": 100.0,
                    "current_frame": total_frames,
                    "total_frames": total_frames,
                    "message": f"YOLO detection completed. Processed {processed_count} frames.",
                },
            )

    except (VideoProcessingError, DetectionError) as e:
        print(f"Detection error: {e}")
        session = db.query(AnalysisSession).filter(AnalysisSession.id == session_id).first()
        if session:
            session.status = "ERROR"
            db.commit()
        await ws_manager.broadcast_to_session(
            session_id,
            {
                "type": "processing_status",
                "session_id": session_id,
                "status": "error",
                "progress": 0.0,
                "message": f"Detection failed: {str(e)}",
            },
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Unexpected error: {e}")
        session = db.query(AnalysisSession).filter(AnalysisSession.id == session_id).first()
        if session:
            session.status = "ERROR"
            db.commit()
        await ws_manager.broadcast_to_session(
            session_id,
            {
                "type": "processing_status",
                "session_id": session_id,
                "status": "error",
                "progress": 0.0,
                "message": f"Unexpected error during detection: {str(e)}",
            },
        )

    finally:
        db.close()
