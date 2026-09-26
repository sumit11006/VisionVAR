def test_formation_returns_not_implemented(client):
    response = client.get("/api/matches/UCL-2024-MCI-RMA-F/formation")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "not_implemented"
    assert data["module"] == "FormationService"
    assert "not implemented" in data["message"].lower()
    assert "expected_payload" in data["contract_specification"]


def test_offside_returns_not_implemented(client):
    response = client.get("/api/matches/UCL-2024-MCI-RMA-F/offside")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "not_implemented"
    assert data["module"] == "OffsideService"
    assert "not implemented" in data["message"].lower()
    assert "expected_payload" in data["contract_specification"]
