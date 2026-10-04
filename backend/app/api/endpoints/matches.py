from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.schemas.match import MatchResponse
from backend.app.schemas.event import MatchEventsListResponse
from backend.app.schemas.player import PlayerTelemetryResponse
from backend.app.services.match_service import MatchService
from backend.app.core.database import get_db
import json
from pathlib import Path
from backend.app.models.session import AnalysisSession

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

@router.get(
    "/{match_id}/analytics",
    tags=["Analytics"],
    summary="Get full match player and team analytics",
)
def get_match_analytics(match_id: str, db: Session = Depends(get_db)):
    """Retrieve tracking-based distance, speed, and event counts for all players."""
    session = db.query(AnalysisSession).filter(
        (AnalysisSession.match_id == match_id) | (AnalysisSession.id == match_id)
    ).order_by(AnalysisSession.created_at.desc()).first()
    if not session:
        return {"players": [], "teams": []}
    
    from backend.app.core.config import settings
    analytics_file = Path(settings.SESSIONS_DIR) / session.id / "analytics.json"
    if not analytics_file.exists():
        return {"players": [], "teams": []}
        
    with open(analytics_file, "r") as f:
        return json.load(f)

@router.get(
    "/{match_id}/summary",
    tags=["Analytics"],
    summary="Get aggregated match summary layer",
)
def get_match_summary(match_id: str, db: Session = Depends(get_db)):
    """Retrieve full match tactical intelligence and aggregate events."""
    session = db.query(AnalysisSession).filter(
        (AnalysisSession.match_id == match_id) | (AnalysisSession.id == match_id)
    ).order_by(AnalysisSession.created_at.desc()).first()
    if not session:
        return {}
    
    from backend.app.core.config import settings
    summary_file = Path(settings.SESSIONS_DIR) / session.id / "match_summary.json"
    if not summary_file.exists():
        return {}
        
    with open(summary_file, "r", encoding="utf-8") as f:
        return json.load(f)

@router.get(
    "/{match_id}/players/{player_id}/analytics",
    tags=["Analytics"],
    summary="Get individual player analytics",
)
def get_player_analytics(match_id: str, player_id: str, db: Session = Depends(get_db)):
    """Retrieve full analytics payload for a specific player."""
    data = get_match_analytics(match_id, db)
    for p in data.get("players", []):
        if str(p.get("player_id")) == str(player_id):
            return p
    return {}

@router.get(
    "/{match_id}/players/{player_id}/heatmap",
    tags=["Analytics"],
    summary="Get individual player movement heatmap",
)
def get_player_heatmap(match_id: str, player_id: str, db: Session = Depends(get_db)):
    """Retrieve heatmap coordinates for a specific player."""
    p_data = get_player_analytics(match_id, player_id, db)
    return p_data.get("heatmap", [])

@router.get(
    "/{match_id}/teams/{team_code}/analytics",
    tags=["Analytics"],
    summary="Get team-level aggregated analytics",
)
def get_team_analytics(match_id: str, team_code: str, db: Session = Depends(get_db)):
    """Retrieve aggregated distance, passes, touches for a specific team."""
    data = get_match_analytics(match_id, db)
    for t in data.get("teams", []):
        if t.get("team_name") == team_code:
            return t
    return {}
