import pytest
import json
from pathlib import Path
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.config import settings
import os

client = TestClient(app)

@pytest.fixture
def mock_tracking_results():
    """Create a mock tracking_results.json for a test session."""
    session_id = "test_vod_session"
    session_dir = Path(settings.SESSIONS_DIR) / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = session_dir / "tracking_results.json"
    
    data = {
        "session_id": session_id,
        "frames": [
            {
                "frame_number": 0,
                "timestamp": 0.0,
                "tracked_items": [
                    {
                        "track_id": 1,
                        "class_name": "player",
                        "confidence": 0.95,
                        "bbox": {"x1": 10, "y1": 10, "x2": 20, "y2": 30},
                        "team": "team_a",
                        "mapping_status": "mapped"
                    }
                ],
                "ball_state": {
                    "state": "tracked",
                    "confidence": 0.88,
                    "bbox": [5, 5, 15, 15]
                },
                "formation": {},
                "pitch_mapping_status": "mapped"
            }
        ]
    }
    
    with open(file_path, "w") as f:
        json.dump(data, f)
        
    yield session_id
    
    # Cleanup
    if file_path.exists():
        file_path.unlink()
    if session_dir.exists():
        session_dir.rmdir()

def test_get_tracking_history_success(mock_tracking_results):
    session_id = mock_tracking_results
    response = client.get(f"/api/analysis/sessions/{session_id}/tracking")
    assert response.status_code == 200
    
    data = response.json()
    assert data["session_id"] == session_id
    assert len(data["frames"]) == 1
    
    frame = data["frames"][0]
    assert frame["frame_number"] == 0
    assert frame["timestamp"] == 0.0
    assert "tracked_items" in frame
    assert "ball_state" in frame
    assert "formation" in frame
    assert "pitch_mapping_status" in frame

def test_get_tracking_history_not_found():
    response = client.get("/api/analysis/sessions/non_existent_session/tracking")
    assert response.status_code == 404
