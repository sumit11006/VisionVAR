from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.schemas.match import MatchResponse
from backend.app.schemas.event import MatchEventsListResponse
from backend.app.schemas.player import PlayerTelemetryResponse
from backend.app.services.match_service import MatchService
from backend.app.core.database import get_db

router = APIRouter()


@router.get(
    "/{match_id}",
    response_model=MatchResponse,
    tags=["Matches"],
    summary="Get match context and scoreboard",
)
def get_match(match_id: str, db: Session = Depends(get_db)):
    """Retrieve full match context including teams, score, clock, competition, and optical feed spec."""
    service = MatchService(db)
    return service.get_match(match_id)


@router.get(
    "/{match_id}/events",
    response_model=MatchEventsListResponse,
    tags=["Matches"],
    summary="Get match timeline events",
)
def get_match_events(match_id: str, db: Session = Depends(get_db)):
    """Retrieve chronologically ordered events (goals, fouls, offsides, VAR reviews, substitutions)."""
    service = MatchService(db)
    return service.get_events(match_id)


@router.get(
    "/{match_id}/players/{player_id}/telemetry",
    response_model=PlayerTelemetryResponse,
    tags=["Players"],
    summary="Get player spatial telemetry and physical metrics",
)
def get_player_telemetry(
    match_id: str,
    player_id: str,
    db: Session = Depends(get_db),
):
    """Retrieve individual player skeletal tracking confidence, sprint counts, speed, and 3D coordinates."""
    service = MatchService(db)
    return service.get_player_telemetry(match_id, player_id)
