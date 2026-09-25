import os
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from backend.app.models.video import Video
from backend.app.models.session import AnalysisSession
from backend.app.core.config import settings
from backend.cv.video_processor import VideoProcessor


class VideoService:
    ALLOWED_EXTENSIONS = {".mp4", ".mkv", ".mov", ".avi", ".ts"}

    def __init__(self, db: Session):
        self.db = db
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def save_upload(self, file: UploadFile) -> Video:
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename cannot be empty")

        ext = Path(file.filename).suffix.lower()
        if ext not in self.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported video format: '{ext}'. Supported formats: {list(self.ALLOWED_EXTENSIONS)}",
            )

        video_id = f"vid_{uuid.uuid4().hex[:12]}"
        saved_filename = f"{video_id}_{file.filename}"
        target_path = self.upload_dir / saved_filename

        total_bytes = 0
        with open(target_path, "wb") as out_file:
            while chunk := await file.read(1024 * 1024):  # 1MB chunks
                total_bytes += len(chunk)
                out_file.write(chunk)

        # Extract real OpenCV video metadata immediately
        fps = None
        total_frames = None
        duration_seconds = None
        resolution = None

        try:
            with VideoProcessor(target_path) as vp:
                meta = vp.metadata
                fps = meta["fps"]
                total_frames = meta["total_frames"]
                duration_seconds = meta["duration_seconds"]
                resolution = meta["resolution"]
        except Exception:
            # Fallback if file is synthetic/corrupt in test
            pass

        video = Video(
            id=video_id,
            filename=file.filename,
            file_path=str(target_path),
            file_size_bytes=total_bytes,
            content_type=file.content_type or "video/mp4",
            duration_seconds=duration_seconds,
            fps=fps,
            total_frames=total_frames,
            resolution=resolution,
            status="READY" if fps and fps > 0 else "UPLOADED",
        )
        self.db.add(video)

        # Create a dedicated Match and AnalysisSession for this uploaded video
        clean_name = Path(file.filename).stem.replace("_", " ").replace("-", " ").title()
        match_id = f"match_{video_id}"
        from backend.app.models.match import Match
        match = Match(
            id=match_id,
            home_team_code="VID",
            home_team_name=clean_name[:24] if clean_name else "Uploaded Match",
            away_team_code="VAR",
            away_team_name="AI Video Analysis",
            competition="Custom Match Ingestion",
            venue=f"Source: {file.filename}",
            status="COMPLETE",
            feed_spec=f"{resolution or 'HD'} • {round(fps or 30.0, 1)} FPS",
        )
        self.db.add(match)

        session_id = f"session_{video_id}"
        analysis_session = AnalysisSession(
            id=session_id,
            match_id=match_id,
            video_id=video_id,
            status="READY",
            progress_percent=100,
            current_stage="COMPLETE",
            eta_minutes=0,
            camera_sources="Optical Match Feed",
        )
        self.db.add(analysis_session)

        self.db.commit()
        self.db.refresh(video)
        return video

    def ensure_metadata(self, video: Video) -> Video:
        """Ensures OpenCV metadata (FPS, frames, duration, resolution) is populated for a video."""
        if (
            video.duration_seconds is None
            or video.fps is None
            or video.total_frames is None
            or video.resolution is None
        ):
            file_path = Path(video.file_path)
            if file_path.exists():
                try:
                    with VideoProcessor(file_path) as vp:
                        meta = vp.metadata
                        video.fps = meta["fps"]
                        video.total_frames = meta["total_frames"]
                        video.duration_seconds = meta["duration_seconds"]
                        video.resolution = meta["resolution"]
                        video.status = "READY"
                        self.db.commit()
                        self.db.refresh(video)
                except Exception:
                    pass
        return video

    def get_video(self, video_id: str) -> Video:
        video = self.db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise HTTPException(status_code=404, detail=f"Video with id '{video_id}' not found.")
        return self.ensure_metadata(video)
