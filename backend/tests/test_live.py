import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_live_start_and_status():
    # 1. Start live session
    res = client.post("/api/live/start", json={
        "source": "test_video.mp4",
        "target_fps": 15.0
    })
    assert res.status_code == 200
    data = res.json()
    assert "session_id" in data
    session_id = data["session_id"]
    
    # 2. Get status
    res = client.get(f"/api/live/{session_id}/status")
    assert res.status_code == 200
    status = res.json()
    assert "is_running" in status
    
    # 3. Stop live session
    res = client.post(f"/api/live/{session_id}/stop")
    assert res.status_code == 200
    
    # 4. Try stopping again
    res = client.post(f"/api/live/{session_id}/stop")
    assert res.status_code == 404
