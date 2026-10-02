from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid

from backend.app.core.database import get_db
from backend.app.models.session import AnalysisSession
from backend.app.schemas.live import LiveStartRequest, LiveSessionResponse
from backend.app.services.live_runner import start_live_session, stop_live_session, get_live_status

router = APIRouter()

@router.post("/start", response_model=LiveSessionResponse)
async def start_live(req: LiveStartRequest, db: Session = Depends(get_db)):
    session_id = f"live_{uuid.uuid4().hex[:8]}"
    
    # Create session in DB
    db_session = AnalysisSession(
        id=session_id,
        match_id=req.match_id,
        status="STARTING",
        current_stage="INIT",
        progress_percent=0,
        camera_sources=req.source
    )
    db.add(db_session)
    db.commit()
    
    success = await start_live_session(session_id, req.source, req.target_fps or 15.0)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to start live session")
        
    return LiveSessionResponse(
        session_id=session_id,
        status="running",
        source=req.source,
        message="Live session started"
    )

@router.post("/{session_id}/stop")
async def stop_live(session_id: str, db: Session = Depends(get_db)):
    success = await stop_live_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Active live session not found")
        
    # Update DB
    db_session = db.query(AnalysisSession).filter(AnalysisSession.id == session_id).first()
    if db_session:
        db_session.status = "COMPLETED"
        db.commit()
        
    return {"message": "Live session stopped"}

@router.get("/{session_id}/status")
async def live_status(session_id: str):
    status = get_live_status(session_id)
    if not status:
        raise HTTPException(status_code=404, detail="Active live session not found")
    return status
