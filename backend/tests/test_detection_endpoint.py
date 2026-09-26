def test_start_detection_valid_session(client):
    session_id = "UCL-2024-MCI-RMA-F"
    response = client.post(
        f"/api/analysis/sessions/{session_id}/detect",
        json={"frame_skip": 2, "confidence_threshold": 0.3},
    )
    assert response.status_code == 202
    data = response.json()
    assert data["session_id"] == session_id
    assert data["status"] == "processing"
    assert "YOLO" in data["message"]


def test_start_detection_nonexistent_session(client):
    response = client.post(
        "/api/analysis/sessions/invalid-session-99999/detect",
        json={"frame_skip": 1},
    )
    assert response.status_code == 404
