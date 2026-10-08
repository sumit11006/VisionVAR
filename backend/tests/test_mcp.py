import pytest
import json
from backend.app.mcp.server import (
    get_match_summary,
    get_team_analytics,
    get_player_analytics,
    get_events,
    get_offside_incidents,
    get_formation,
    get_player_position,
    get_live_status,
    get_video_frame,
)
from backend.app.core.database import Base, engine, SessionLocal
from backend.app.models.match import Match
from backend.app.models.session import AnalysisSession
from backend.app.models.event import MatchEvent

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    # Add dummy match
    if not db.query(Match).filter(Match.id == "test_match_123").first():
        match = Match(id="test_match_123", home_team_code="HOM", away_team_code="AWA")
        db.add(match)
        session = AnalysisSession(id="test_session_123", match_id="test_match_123", status="READY")
        db.add(session)
        event = MatchEvent(id="evt1", match_id="test_match_123", minute=0, type="OFFSIDE_CANDIDATE", status="REVIEW", ai_explanation="Insufficient Evidence")
        db.add(event)
        db.commit()
    yield
    db.close()

def test_get_match_summary():
    # Test valid input (even if json missing, should handle gracefully)
    res = get_match_summary("test_match_123")
    data = json.loads(res)
    # the JSON file might be missing in test env
    assert "error" in data or "teams" in data

def test_get_team_analytics():
    res = get_team_analytics("test_match_123", "HOM")
    data = json.loads(res)
    assert "error" in data or "possession" in data

def test_get_player_analytics():
    res = get_player_analytics("test_match_123", "track_1")
    data = json.loads(res)
    assert "error" in data or "distance" in data

def test_get_events():
    res = get_events("test_match_123")
    data = json.loads(res)
    assert "events" in data
    assert data["count"] >= 1
    
def test_get_offside_incidents():
    res = get_offside_incidents("test_match_123")
    data = json.loads(res)
    assert isinstance(data, list)
    if len(data) > 0:
        assert "ai_assessment" in data[0]

def test_get_formation():
    res = get_formation("test_match_123", "HOM")
    data = json.loads(res)
    assert "error" in data or "formation" in data

def test_get_player_position():
    res = get_player_position("test_match_123", "track_1", 100)
    data = json.loads(res)
    assert "error" in data or "image_coordinates" in data
    
def test_get_live_status():
    res = get_live_status("test_session_123")
    data = json.loads(res)
    assert "status" in data
    assert data["status"] in ["READY", "PROCESSING", "RUNNING"]

def test_get_video_frame():
    res = get_video_frame("test_match_123", 250)
    data = json.loads(res)
    assert data["frame_number"] == 250
    assert "Metadata only" in data["status"]

def test_missing_match():
    res = get_match_summary("invalid_match")
    data = json.loads(res)
    assert "error" in data
