def test_list_sessions(client):
    response = client.get("/api/analysis/sessions")
    assert response.status_code == 200
    sessions = response.json()
    assert len(sessions) >= 3
    # Check default seeded session
    ucl = next(s for s in sessions if s["id"] == "UCL-2024-MCI-RMA-F")
    assert ucl["homeTeam"] == "Manchester City"
    assert ucl["status"] == "READY"


def test_create_session(client):
    payload = {
        "match_id": "UCL-2024-MCI-RMA-F",
        "competition": "UEFA Champions League",
        "camera_sources": "12-CAM OPTICAL ARRAY",
    }
    response = client.post("/api/analysis/sessions", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "session_" in data["id"]
    assert data["status"] == "PROCESSING"


def test_get_session_by_id(client):
    response = client.get("/api/analysis/sessions/UCL-2024-MCI-RMA-F")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "UCL-2024-MCI-RMA-F"
    assert data["varAlerts"] == 14


def test_get_session_not_found(client):
    response = client.get("/api/analysis/sessions/non-existent-session")
    assert response.status_code == 404


def test_get_session_status(client):
    response = client.get("/api/analysis/sessions/UCL-2024-MCI-RMA-F/status")
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == "UCL-2024-MCI-RMA-F"
    assert data["status"] == "READY"
    assert data["progress_percent"] == 100


def test_session_has_video_metadata_field(client):
    response = client.get("/api/analysis/sessions/UCL-2024-MCI-RMA-F")
    assert response.status_code == 200
    data = response.json()
    assert "video_metadata" in data

