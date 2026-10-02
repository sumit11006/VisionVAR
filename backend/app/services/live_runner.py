import asyncio
import cv2
import time
import json
import uuid
from typing import Dict, Any, Optional
from pathlib import Path
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.database import SessionLocal
from backend.app.models.session import AnalysisSession
from backend.app.models.event import MatchEvent
from backend.app.websocket.manager import ws_manager

from backend.cv.detection.service import DetectionService
from backend.cv.tracking.tracking_service import TrackingService
from backend.cv.ball.service import BallTrackingService
from backend.cv.team.service import TeamClassificationService
from backend.cv.pitch.service import PitchMappingService
from backend.cv.formation.service import FormationService
from backend.cv.events.ball_contact import BallContactService
from backend.cv.offside.service import OffsideAnalysisService
from backend.cv.events.service import EventDetectionService
from backend.cv.events.pass_detection import PassDetectionService
from backend.cv.events.shot_detection import ShotDetectionService
from backend.cv.events.goal_detection import GoalDetectionService
from backend.cv.events.possession import PossessionService
from backend.cv.analytics.player_analytics import PlayerAnalyticsService
from backend.cv.analytics.match_summary import MatchSummaryService

class LiveAnalysisRunner:
    def __init__(self, session_id: str, source: str, target_fps: float = 15.0):
        self.session_id = session_id
        self.source = source
        self.target_fps = target_fps
        self.is_running = False
        
        # State
        self.processed_count = 0
        self.dropped_count = 0
        self.start_time = 0
        self.last_frame_time = 0
        self.source_fps = 0.0
        
        # Services
        self.detector = None
        self.tracker = None
        self.ball_tracker = None
        self.team_classifier = None
        self.pitch_mapper = None
        self.formation_analyzer = None
        self.ball_contact_analyzer = None
        self.offside_analyzer = None
        self.event_detector = None
        self.pass_detector = None
        self.shot_detector = None
        self.goal_detector = None
        self.possession_tracker = None
        self.player_analytics = None

    async def start(self):
        self.is_running = True
        asyncio.create_task(self._run_loop())

    async def stop(self):
        self.is_running = False

    async def _run_loop(self):
        db = SessionLocal()
        session = db.query(AnalysisSession).filter(AnalysisSession.id == self.session_id).first()
        if not session:
            db.close()
            return
            
        session.status = "LIVE"
        session.current_stage = "LIVE_PROCESSING"
        db.commit()
        
        # Initialize Services
        self.detector = DetectionService(confidence_threshold=0.3)
        self.tracker = TrackingService()
        self.ball_tracker = BallTrackingService()
        self.team_classifier = TeamClassificationService()
        self.pitch_mapper = PitchMappingService()
        self.formation_analyzer = FormationService()
        self.ball_contact_analyzer = BallContactService()
        self.offside_analyzer = OffsideAnalysisService()
        self.event_detector = EventDetectionService()
        self.pass_detector = PassDetectionService()
        self.shot_detector = ShotDetectionService()
        self.goal_detector = GoalDetectionService()
        self.possession_tracker = PossessionService(distance_threshold_m=2.5, firm_possession_frames=5)
        
        src = self.source
        if src.isdigit():
            src = int(src)
        elif not src.startswith("http") and not src.startswith("rtsp"):
            # Assume local file in uploads if not absolute
            if not Path(src).is_absolute():
                src = str(Path(settings.UPLOAD_DIR) / src)
                
        cap = cv2.VideoCapture(src)
        if not cap.isOpened():
            session.status = "ERROR"
            db.commit()
            db.close()
            await ws_manager.broadcast_to_session(self.session_id, {"type": "ERROR", "message": "Failed to open source"})
            return

        self.source_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        if self.source_fps <= 0:
            self.source_fps = 30.0
            
        self.player_analytics = PlayerAnalyticsService(fps=self.target_fps)

        self.start_time = time.time()
        self.last_frame_time = time.time()
        frame_idx = 0
        target_frame_time = 1.0 / self.target_fps
        
        try:
            while self.is_running:
                loop_start = time.time()
                
                ret, frame_bgr = cap.read()
                if not ret:
                    if isinstance(src, str) and not src.startswith("http") and not src.startswith("rtsp"):
                        # Loop local video to simulate continuous live stream
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        continue
                    else:
                        break # Stream ended/disconnected
                
                frame_idx += 1
                current_time = time.time()
                elapsed_since_last = current_time - self.last_frame_time
                
                # Frame dropping logic to maintain target FPS
                if elapsed_since_last < target_frame_time:
                    self.dropped_count += 1
                    # Skip frame
                    continue
                    
                self.last_frame_time = current_time
                timestamp = frame_idx / self.source_fps
                
                # --- Pipeline processing ---
                t_det_start = time.time()
                # Run detection in thread to avoid blocking asyncio
                frame_result = await asyncio.to_thread(self.detector.detect_frame, frame_bgr, frame_idx)
                
                t_track_start = time.time()
                tracked_items = self.tracker.update(frame_result.detections, frame_idx, timestamp)
                ball_detections = [d for d in frame_result.detections if d.class_name == "ball"]
                ball_state = self.ball_tracker.update(ball_detections, frame_idx, timestamp)
                
                tracked_items = self.team_classifier.process_tracked_items(tracked_items, frame_bgr)
                
                for item in tracked_items:
                    pitch_pos = self.pitch_mapper.project_player({"x1": item.bbox.x1, "y1": item.bbox.y1, "x2": item.bbox.x2, "y2": item.bbox.y2})
                    if pitch_pos:
                        item.pitch_position = {"x": pitch_pos["x"], "y": pitch_pos["y"]}

                if ball_state.get("state") in ["tracked", "reacquired"] and ball_state.get("bbox"):
                    ball_pitch_pos = self.pitch_mapper.project_player(ball_state["bbox"])
                    if ball_pitch_pos:
                        ball_state["pitch_position"] = {"x": ball_pitch_pos["x"], "y": ball_pitch_pos["y"]}
                
                # Formation
                formation = self.formation_analyzer.process_frame(tracked_items)
                
                # Events
                contact = self.ball_contact_analyzer.process_frame(ball_state, frame_idx, timestamp)
                offside = self.offside_analyzer.analyze(contact, tracked_items, timestamp, frame_idx)
                
                events = []
                detected_events = self.event_detector.process(
                    frame_idx=frame_idx,
                    timestamp=timestamp,
                    session_id=self.session_id,
                    match_id=session.match_id,
                    tracked_items=tracked_items,
                    ball_state=ball_state,
                    ball_contact_event=contact,
                    offside_candidate=offside,
                )
                
                pass_events = self.pass_detector.process(
                    frame_idx=frame_idx,
                    timestamp=timestamp,
                    session_id=self.session_id,
                    match_id=session.match_id,
                    tracked_items=tracked_items,
                    ball_state=ball_state,
                    ball_contact_event=contact
                )
                
                shot_events = self.shot_detector.process(
                    frame_idx=frame_idx,
                    timestamp=timestamp,
                    session_id=self.session_id,
                    match_id=session.match_id,
                    tracked_items=tracked_items,
                    ball_state=ball_state,
                    ball_contact_event=contact
                )
                
                attacking_directions = {
                    "team_a": self.shot_detector.determine_attacking_direction("team_a", tracked_items),
                    "team_b": self.shot_detector.determine_attacking_direction("team_b", tracked_items)
                }
                
                goal_events = self.goal_detector.process(
                    frame_idx=frame_idx,
                    timestamp=timestamp,
                    session_id=self.session_id,
                    match_id=session.match_id,
                    ball_state=ball_state,
                    attacking_directions=attacking_directions,
                    active_shots=[self.shot_detector.active_shot] if self.shot_detector.active_shot else None
                )
                
                possession_events = self.possession_tracker.process(
                    frame_idx=frame_idx,
                    timestamp=timestamp,
                    tracked_items=tracked_items,
                    ball_state=ball_state,
                    ball_contact_event=contact
                )
                
                import uuid
                for pe in possession_events:
                    pe["id"] = f"evt_{uuid.uuid4().hex[:8]}"
                    pe["match_id"] = session.match_id
                    
                events.extend(detected_events)
                events.extend(pass_events)
                events.extend(shot_events)
                events.extend(goal_events)
                events.extend(possession_events)
                
                # Save events
                for ev in events:
                    db_event = MatchEvent(
                        id=ev["id"],
                        match_id=ev["match_id"],
                        minute=int(ev["timestamp"] // 60),
                        second=int(ev["timestamp"] % 60),
                        frame_id=ev["frame"],
                        type=ev["event_type"],
                        team=ev.get("team", ""),
                        player=ev.get("player"),
                        status=ev.get("status", "candidate"),
                        confidence=ev.get("confidence", 0.0),
                        metadata_json=json.dumps(ev["metadata"]) if ev.get("metadata") else None
                    )
                    db.add(db_event)
                
                db.commit()
                
                # Player analytics
                self.player_analytics.process_frame(frame_idx, timestamp, tracked_items, events)
                self.processed_count += 1
                
                t_end = time.time()
                
                det_latency = (t_track_start - t_det_start) * 1000
                track_latency = (t_end - t_track_start) * 1000
                total_latency = (t_end - loop_start) * 1000
                
                processed_fps = self.processed_count / max(0.1, time.time() - self.start_time)
                
                # Broadcast WS
                await ws_manager.broadcast_to_session(self.session_id, {
                    "type": "FRAME_UPDATE",
                    "session_id": self.session_id,
                    "timestamp": timestamp,
                    "frame": frame_idx
                })
                await ws_manager.broadcast_to_session(self.session_id, {
                    "type": "TRACKING_UPDATE",
                    "session_id": self.session_id,
                    "timestamp": timestamp,
                    "frame": frame_idx,
                    "tracked_items": tracked_items
                })
                await ws_manager.broadcast_to_session(self.session_id, {
                    "type": "BALL_UPDATE",
                    "session_id": self.session_id,
                    "timestamp": timestamp,
                    "frame": frame_idx,
                    "ball": ball_state
                })
                await ws_manager.broadcast_to_session(self.session_id, {
                    "type": "FORMATION_UPDATE",
                    "session_id": self.session_id,
                    "timestamp": timestamp,
                    "frame": frame_idx,
                    "formation": formation
                })
                
                for ev in events:
                    if "possession" in ev["event_type"]:
                        await ws_manager.broadcast_to_session(self.session_id, {
                            "type": "POSSESSION_UPDATE",
                            "session_id": self.session_id,
                            "timestamp": timestamp,
                            "frame": frame_idx,
                            "event": ev
                        })
                    elif ev["event_type"] == "offside_review":
                        await ws_manager.broadcast_to_session(self.session_id, {
                            "type": "OFFSIDE_REVIEW",
                            "session_id": self.session_id,
                            "timestamp": timestamp,
                            "frame": frame_idx,
                            "event": ev
                        })
                    else:
                        await ws_manager.broadcast_to_session(self.session_id, {
                            "type": "EVENT",
                            "session_id": self.session_id,
                            "timestamp": timestamp,
                            "frame": frame_idx,
                            "event": ev
                        })
                
                await ws_manager.broadcast_to_session(self.session_id, {
                    "type": "LIVE_METRICS",
                    "session_id": self.session_id,
                    "timestamp": timestamp,
                    "frame": frame_idx,
                    "metrics": {
                        "source_fps": round(self.source_fps, 1),
                        "processed_fps": round(processed_fps, 1),
                        "dropped_frames": self.dropped_count,
                        "detection_latency_ms": round(det_latency, 1),
                        "tracking_latency_ms": round(track_latency, 1),
                        "total_latency_ms": round(total_latency, 1)
                    }
                })
                
                # Small sleep to yield to event loop
                await asyncio.sleep(0.005)
                
        finally:
            cap.release()
            session.status = "COMPLETED"
            db.commit()
            db.close()
            await ws_manager.broadcast_to_session(self.session_id, {"type": "STREAM_STATUS", "status": "stopped"})

# Simple registry for active live runners
active_live_runners: Dict[str, LiveAnalysisRunner] = {}

async def start_live_session(session_id: str, source: str, target_fps: float):
    if session_id in active_live_runners and active_live_runners[session_id].is_running:
        return False
        
    runner = LiveAnalysisRunner(session_id, source, target_fps)
    active_live_runners[session_id] = runner
    await runner.start()
    return True

async def stop_live_session(session_id: str):
    if session_id in active_live_runners:
        await active_live_runners[session_id].stop()
        del active_live_runners[session_id]
        return True
    return False

def get_live_status(session_id: str):
    if session_id in active_live_runners:
        runner = active_live_runners[session_id]
        return {
            "is_running": runner.is_running,
            "processed_count": runner.processed_count,
            "dropped_count": runner.dropped_count,
            "uptime_seconds": round(time.time() - runner.start_time, 2) if runner.start_time else 0,
        }
    return None
