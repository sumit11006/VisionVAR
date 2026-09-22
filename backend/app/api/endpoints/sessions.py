import asyncio
from typing import List, Optional
from fastapi import APIRouter, Depends, status, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from backend.app.schemas.session import (
    SessionCreateRequest,
    SessionResponse,
    SessionStatusResponse,
)
from backend.app.schemas.detection import (
    DetectionStartRequest,
    DetectionStartResponse,
)
from backend.app.services.session_service import SessionService
from backend.app.services.detection_runner import run_detection_pipeline
from backend.app.models.session import AnalysisSession
from backend.app.models.video import Video
from backend.app.core.database import get_db

router = APIRouter()


@router.get(
    "/sessions",
    response_model=List[SessionResponse],
    tags=["Analysis Sessions"],
    summary="List all match analysis sessions",
)
def list_sessions(db: Session = Depends(get_db)):
    """Retrieve all match analysis sessions ordered by creation date."""
    service = SessionService(db)
    sessions = service.list_sessions()
    return [service.to_schema(s) for s in sessions]


@router.post(
    "/sessions",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Analysis Sessions"],
    summary="Create a new match analysis session",
)
def create_session(
    payload: SessionCreateRequest,
    db: Session = Depends(get_db),
):
    """
    Initializes a new analysis session for an uploaded video or match ID.
    Transitions into PENDING/PROCESSING status for CV queue execution.
    """
    service = SessionService(db)
    session = service.create_session(payload)
    return service.to_schema(session)


@router.get(
    "/sessions/{session_id}",
    response_model=SessionResponse,
    tags=["Analysis Sessions"],
    summary="Get analysis session details",
)
def get_session(session_id: str, db: Session = Depends(get_db)):
    """Retrieve metadata, alerts, and operational stats for a specific analysis session."""
    service = SessionService(db)
    session = service.get_session(session_id)
    return service.to_schema(session)


@router.get(
    "/sessions/{session_id}/status",
    response_model=SessionStatusResponse,
    tags=["Analysis Sessions"],
    summary="Get analysis processing status",
)
def get_session_status(session_id: str, db: Session = Depends(get_db)):
    """Get the live progress percent, active pipeline stage, and ETA for a session."""
    service = SessionService(db)
    return service.get_status(session_id)


@router.post(
    "/sessions/{session_id}/detect",
    response_model=DetectionStartResponse,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Computer Vision Detection"],
    summary="Start real YOLO video detection",
)
async def start_video_detection(
    session_id: str,
    payload: Optional[DetectionStartRequest] = None,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
):
    """
    Initiates real YOLO player & ball detection on the video associated with the session.
    Runs asynchronously in the background and broadcasts frame-by-frame detections
    over WebSocket at /ws/analysis/{session_id}.
    """
    session = db.query(AnalysisSession).filter(AnalysisSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail=f"Analysis session '{session_id}' not found.")

    video_id = payload.video_id if payload else None
    frame_skip = payload.frame_skip if payload else None
    conf_threshold = payload.confidence_threshold if payload else None

    # Enqueue background detection task asynchronously
    asyncio.create_task(
        run_detection_pipeline(
            session_id=session_id,
            video_id=video_id,
            frame_skip=frame_skip,
            conf_threshold=conf_threshold,
        )
    )

    video = None
    if video_id:
        video = db.query(Video).filter(Video.id == video_id).first()
    elif session.video_id:
        video = db.query(Video).filter(Video.id == session.video_id).first()
    else:
        video = db.query(Video).order_by(Video.created_at.desc()).first()

    return DetectionStartResponse(
        session_id=session_id,
        status="processing",
        total_frames=video.total_frames if video else None,
        fps=video.fps if video else None,
        duration_seconds=video.duration_seconds if video else None,
        message="YOLO player & ball detection initiated in background. Connect to WebSocket /ws/analysis/{session_id} for live stream.",
    )
