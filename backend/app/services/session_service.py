import uuid
from typing import List, Optional
from pathlib import Path
from fastapi import HTTPException
from sqlalchemy.orm import Session
from backend.app.models.session import AnalysisSession
from backend.app.models.match import Match
from backend.app.models.video import Video
from backend.app.schemas.session import SessionCreateRequest, SessionResponse, SessionStatusResponse, VideoMetadata
from backend.cv.video_processor import VideoProcessor


class SessionService:
    def __init__(self, db: Session):
        self.db = db

    def list_sessions(self) -> List[AnalysisSession]:
        return self.db.query(AnalysisSession).order_by(AnalysisSession.created_at.desc()).all()

    def get_session(self, session_id: str) -> AnalysisSession:
        session = self.db.query(AnalysisSession).filter(AnalysisSession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail=f"Analysis session '{session_id}' not found.")
        return session

    def create_session(self, req: SessionCreateRequest) -> AnalysisSession:
        session_id = f"session_{uuid.uuid4().hex[:10]}"

        # If a match_id is provided, verify it exists or link to it
        match_id = req.match_id
        if match_id:
            match = self.db.query(Match).filter(Match.id == match_id).first()
            if not match:
                # Create a placeholder match if not existing
                match = Match(
                    id=match_id,
                    home_team_name=req.home_team or "Home Team",
                    away_team_name=req.away_team or "Away Team",
                    competition=req.competition or "Match Analysis",
                    venue=req.venue or "Stadium",
                )
                self.db.add(match)
                self.db.flush()

        session = AnalysisSession(
            id=session_id,
            match_id=match_id,
            video_id=req.video_id,
            status="PROCESSING",
            progress_percent=5,
            current_stage="INGESTION_AND_EXTRACTION",
            eta_minutes=2,
            camera_sources=req.camera_sources or "12-CAM OPTICAL ARRAY",
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_status(self, session_id: str) -> SessionStatusResponse:
        session = self.get_session(session_id)
        return SessionStatusResponse(
            session_id=session.id,
            status=session.status,
            progress_percent=session.progress_percent,
            current_stage=session.current_stage,
            eta_minutes=session.eta_minutes,
            detail=f"Pipeline is at stage: {session.current_stage} ({session.progress_percent}% complete).",
        )

    def to_schema(self, session: AnalysisSession) -> SessionResponse:
        # Resolve home / away team names from associated match or defaults
        home_name = session.match.home_team_name if session.match else "Home Team"
        away_name = session.match.away_team_name if session.match else "Away Team"
        comp = session.match.competition if session.match else "VisionVAR Match"
        ven = session.match.venue if session.match else "Main Stadium"

        # Resolve video and its OpenCV metadata strictly for this session
        video = session.video
        if not video and session.video_id:
            video = self.db.query(Video).filter(Video.id == session.video_id).first()

        video_meta: Optional[VideoMetadata] = None
        if video:
            # Ensure metadata is extracted
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
                            self.db.commit()
                            self.db.refresh(video)
                    except Exception:
                        pass

            # Extract width / height
            width = 1280
            height = 720
            if video.resolution and "x" in video.resolution:
                parts = video.resolution.split("x")
                if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                    width = int(parts[0])
                    height = int(parts[1])

            video_meta = VideoMetadata(
                video_id=video.id,
                filename=video.filename,
                fps=video.fps or 30.0,
                total_frames=video.total_frames or (int((video.duration_seconds or 0) * (video.fps or 30))),
                duration_seconds=video.duration_seconds or 0.0,
                resolution=video.resolution or f"{width}x{height}",
                width=width,
                height=height,
            )

        return SessionResponse(
            id=session.id,
            match_id=session.match_id,
            video_id=session.video_id,
            homeTeam=home_name,
            awayTeam=away_name,
            competition=comp,
            venue=ven,
            status=session.status,
            imageUrl=session.image_url,
            varAlerts=session.var_alerts,
            offsideChecks=session.offside_checks,
            penaltyRadar=session.penalty_radar,
            redCardEval=session.red_card_eval,
            goalVerify=session.goal_verify,
            avgOverturnSeconds=session.avg_overturn_seconds,
            processingPercent=session.progress_percent if session.status == "PROCESSING" else None,
            etaMinutes=session.eta_minutes if session.status == "PROCESSING" else None,
            cameraSources=session.camera_sources,
            video_metadata=video_meta,
            createdAt=session.created_at,
            updatedAt=session.updated_at,
        )
