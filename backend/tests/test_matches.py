def test_get_match_info(client):
    response = client.get("/api/matches/UCL-2024-MCI-RMA-F")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "UCL-2024-MCI-RMA-F"
    assert data["homeTeam"]["code"] == "MCI"
    assert data["awayTeam"]["code"] == "RMA"
    assert data["score"]["home"] == 2
    assert data["score"]["away"] == 1
    assert data["status"] == "LIVE"


def test_get_match_events(client):
    response = client.get("/api/matches/UCL-2024-MCI-RMA-F/events")
    assert response.status_code == 200
    data = response.json()
    assert data["match_id"] == "UCL-2024-MCI-RMA-F"
    assert data["total_events"] >= 10
    # First event is Haaland's goal
    first_event = data["events"][0]
    assert first_event["type"] == "GOAL"
    assert first_event["player"] == "Erling Haaland"


def test_get_player_telemetry(client):
    response = client.get("/api/matches/UCL-2024-MCI-RMA-F/players/849-19/telemetry")
    assert response.status_code == 200
    data = response.json()
    assert data["player_id"] == "849-19"
    assert data["name"] == "Mason Mount"
    assert data["jersey"] == 19
    assert data["stats"]["distanceKm"] == 8.42
    assert data["ai_confidence"] == 98.8
    assert "pitch_x" in data["pitch_coordinates"]


def test_get_player_not_found(client):
    response = client.get("/api/matches/UCL-2024-MCI-RMA-F/players/non-existent-player/telemetry")
    assert response.status_code == 404
