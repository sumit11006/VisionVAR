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

        with VideoProcessor(video.file_path) as vp:
            total_frames = vp.total_frames
            fps = vp.fps

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
                tracked_items = tracker.update(frame_result.detections, frame_idx, timestamp)
                tracking_ms = round((time.time() - t1) * 1000, 1)

                # Stream frame detection over WebSocket
                await ws_manager.broadcast_to_session(
                    session_id,
                    {
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
                        "tracked_items": [t.model_dump(by_alias=True) for t in tracked_items],
                    },
                )

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
