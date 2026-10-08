import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_create_session_with_invalid_video():
    payload = {
        "video_id": "non_existent_video_123",
        "home_team": "Team A",
        "away_team": "Team B"
    }
    response = client.post("/api/analysis/sessions", json=payload)
    assert response.status_code == 400
    assert "Video 'non_existent_video_123' not found." in response.json()["detail"]

def test_create_session_with_valid_video():
    # First get an existing video
    response = client.get("/api/videos")
    if response.status_code == 200 and len(response.json()) > 0:
        video_id = response.json()[0]["id"]
        
        payload = {
            "video_id": video_id,
            "home_team": "Team A",
            "away_team": "Team B"
        }
        create_resp = client.post("/api/analysis/sessions", json=payload)
        assert create_resp.status_code == 201
        
        data = create_resp.json()
        assert data["video_id"] == video_id
        
        # Verify get session returns linked video metadata
        session_id = data["id"]
        get_resp = client.get(f"/api/analysis/sessions/{session_id}")
        assert get_resp.status_code == 200
        get_data = get_resp.json()
        assert get_data["video_id"] == video_id
        assert get_data["video_metadata"] is not None
        assert get_data["video_metadata"]["video_id"] == video_id
