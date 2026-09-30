import pytest
from backend.cv.formation.service import FormationService
from backend.app.schemas.detection import TrackedItem, BoundingBox

@pytest.fixture
def formation_service():
    return FormationService(history_frames=5, smoothing_window=3)

def create_mock_player(track_id: int, team: str, x: float, y: float, mapped: bool = True):
    return {
        "track_id": track_id,
        "class_name": "player",
        "team": team,
        "mapping_status": "mapped" if mapped else "unavailable",
        "pitch_position": {"x": x, "y": y}
    }

def test_insufficient_players(formation_service):
    # Pass only 6 players (needs 7 to estimate)
    players = [create_mock_player(i, "team_a", i*10, 30) for i in range(6)]
    formation, conf = formation_service.estimate_team_formation("team_a", players)
    
    assert formation == "Formation unavailable"
    assert conf == 0.0

def test_formation_estimation(formation_service):
    # Let's create 10 players for team A defending the left side (x < 52.5)
    # We want a 4-3-3 formation.
    # 4 defenders near x=10
    # 3 midfielders near x=30
    # 3 attackers near x=50
    players = []
    
    # Defenders
    for i in range(4):
        players.append(create_mock_player(i, "team_a", 10.0 + i*0.1, 20.0 + i*5))
        
    # Midfielders
    for i in range(3):
        players.append(create_mock_player(10+i, "team_a", 30.0 + i*0.1, 25.0 + i*5))
        
    # Attackers
    for i in range(3):
        players.append(create_mock_player(20+i, "team_a", 50.0 + i*0.1, 25.0 + i*5))
        
    formation, conf = formation_service.estimate_team_formation("team_a", players)
    
    # Due to deterministic K-Means on these distinct clusters, we should get 4-3-3
    assert formation == "4-3-3"
    assert conf == 1.0  # 10/10

def test_process_frame_integration(formation_service):
    # Pass a mix of team_a, team_b, and unmapped players
    tracked_items = []
    
    # 7 team_a players
    for i in range(7):
        tracked_items.append(create_mock_player(i, "team_a", 15.0, 30.0))
        
    # 2 team_b players
    tracked_items.append(create_mock_player(100, "team_b", 80.0, 30.0))
    tracked_items.append(create_mock_player(101, "team_b", 80.0, 40.0))
    
    # 1 unmapped player
    tracked_items.append(create_mock_player(200, "team_a", 0.0, 0.0, mapped=False))
    
    # 1 ball
    tracked_items.append({
        "track_id": 999,
        "class_name": "ball",
        "mapping_status": "mapped",
        "pitch_position": {"x": 50, "y": 30}
    })
    
    result = formation_service.process_frame(tracked_items)
    
    # Team A should have a formation (e.g. 7-0-0 or similar since they are all at x=15)
    # But for the test, we just ensure it's not unavailable.
    assert result["team_a"] != "Formation unavailable"
    
    # Team B only has 2 players, so unavailable
    assert result["team_b"] == "Formation unavailable"
    
    # The tracked items should now have movement_trail attached
    assert "movement_trail" in tracked_items[0]
    assert len(tracked_items[0]["movement_trail"]) == 1

def test_temporal_smoothing(formation_service):
    # Send "4-3-3" twice, then "4-4-2" once. 
    # With a smoothing window of 3, "4-3-3" should be the majority.
    
    # Frame 1: 4-3-3 (requires 10 players)
    def send_433():
        players = []
        for i in range(4): players.append(create_mock_player(i, "team_a", 10.0, 20.0))
        for i in range(3): players.append(create_mock_player(10+i, "team_a", 30.0, 20.0))
        for i in range(3): players.append(create_mock_player(20+i, "team_a", 50.0, 20.0))
        return formation_service.process_frame(players)
        
    def send_442():
        players = []
        for i in range(4): players.append(create_mock_player(i, "team_a", 10.0, 20.0))
        for i in range(4): players.append(create_mock_player(10+i, "team_a", 30.0, 20.0))
        for i in range(2): players.append(create_mock_player(20+i, "team_a", 50.0, 20.0))
        return formation_service.process_frame(players)
        
    res1 = send_433()
    assert res1["team_a"] == "4-3-3"
    
    res2 = send_433()
    assert res2["team_a"] == "4-3-3"
    
    # Send a noisy frame (4-4-2)
    res3 = send_442()
    
    # Since 4-3-3 is 2/3 of the history, it should still output 4-3-3
    assert res3["team_a"] == "4-3-3"
