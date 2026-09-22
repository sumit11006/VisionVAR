from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.app.schemas.common import HealthResponse
from backend.app.core.database import get_db

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
def get_health(db: Session = Depends(get_db)):
    """Health check endpoint to verify backend operational readiness and DB connectivity."""
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"

    return HealthResponse(
        status="ok",
        version="1.0.0",
        service="VisionVAR Backend",
        database=db_status,
        cv_pipeline="standby (interfaces mounted)",
    )
