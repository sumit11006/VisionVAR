import pytest
from backend.cv.analytics.player_analytics import PlayerAnalyticsService

def test_distance_and_speed_calculation():
    svc = PlayerAnalyticsService(fps=30.0)
    
    class DummyItem:
        def __init__(self, tid, t, x, y):
            self.class_name = "player"
            self.track_id = tid
            self.team = t
            self.pitch_position = {"x": x, "y": y}
            
    # Frame 1: player at (0, 0)
    item1 = DummyItem(1, "TeamA", 0.0, 0.0)
    svc.process_frame(1, 0.0, [item1], [])
    
    # Frame 2: player at (3, 4) after 1.0 second (dt = 1.0)
    item2 = DummyItem(1, "TeamA", 3.0, 4.0)
    svc.process_frame(2, 1.0, [item2], [])
    
    res = svc.get_summary()
    p1 = res["players"][0]
    
    # Distance should be hypot(3, 4) = 5.0m
    assert p1["estimated_distance_m"] == 5.0
    
    # Tracking duration should be 1.0s (valid dt), not 2 frames
    # Avg speed is total dist / duration = 5.0 / 1.0 = 5.0 m/s
    assert p1["estimated_avg_speed_mps"] == 5.0
    
def test_zero_time_protection():
    svc = PlayerAnalyticsService(fps=30.0)
    class DummyItem:
        def __init__(self, x, y):
            self.class_name = "player"
            self.track_id = 1
            self.team = "TeamA"
            self.pitch_position = {"x": x, "y": y}
            
    svc.process_frame(1, 1.0, [DummyItem(0, 0)], [])
    # Timestamp didn't change (dt = 0)
    svc.process_frame(2, 1.0, [DummyItem(5, 5)], [])
    
    res = svc.get_summary()
    p1 = res["players"][0]
    
    # Distance shouldn't have spiked or thrown division by zero
    assert p1["estimated_distance_m"] == 0.0

def test_event_aggregation():
    svc = PlayerAnalyticsService(fps=30.0)
    class DummyItem:
        def __init__(self):
            self.class_name = "player"
            self.track_id = 1
            self.team = "TeamA"
            self.pitch_position = {"x": 10, "y": 10}
            
    svc.process_frame(1, 1.0, [DummyItem()], [
        {"player": "1", "event_type": "POSSESSION_CANDIDATE"},
        {"player": "1", "event_type": "PASS_CANDIDATE"}
    ])
    
    res = svc.get_summary()
    p1 = res["players"][0]
    assert p1["touches"] == 1
    assert p1["passes"] == 1
    assert round(p1["possession_seconds"], 2) == round(1.0/30.0, 2)
    
def test_team_aggregation():
    svc = PlayerAnalyticsService(fps=30.0)
    class DummyItem:
        def __init__(self, tid, team, x, y):
            self.class_name = "player"
            self.track_id = tid
            self.team = team
            self.pitch_position = {"x": x, "y": y}
            
    svc.process_frame(1, 1.0, [DummyItem(1, "A", 0, 0), DummyItem(2, "A", 0, 0), DummyItem(3, "B", 0, 0)], [])
    svc.process_frame(2, 2.0, [DummyItem(1, "A", 10, 0), DummyItem(2, "A", 0, 10), DummyItem(3, "B", 5, 0)], [])
    
    res = svc.get_summary()
    teams = {t["team_name"]: t for t in res["teams"]}
    
    # Team A: Player 1 moved 10, Player 2 moved 10 -> 20m total
    assert teams["A"]["estimated_distance_m"] == 20.0
    # Team B: Player 3 moved 5 -> 5m total
    assert teams["B"]["estimated_distance_m"] == 5.0

def test_max_speed_gte_average_speed():
    svc = PlayerAnalyticsService(fps=30.0)
    class DummyItem:
        def __init__(self, x, y):
            self.class_name = "player"
            self.track_id = 1
            self.team = "TeamA"
            self.pitch_position = {"x": x, "y": y}
            
    # Move really fast then slow
    svc.process_frame(1, 1.0, [DummyItem(0, 0)], [])
    svc.process_frame(2, 2.0, [DummyItem(10, 0)], []) # 10m/s
    svc.process_frame(3, 3.0, [DummyItem(11, 0)], []) # 1m/s
    
    res = svc.get_summary()
    p1 = res["players"][0]
    assert p1["estimated_max_speed_mps"] >= p1["estimated_avg_speed_mps"]

def test_tracking_gap_split():
    svc = PlayerAnalyticsService(fps=30.0, max_tracking_gap_s=1.0)
    class DummyItem:
        def __init__(self, x, y):
            self.class_name = "player"
            self.track_id = 1
            self.team = "TeamA"
            self.pitch_position = {"x": x, "y": y}
            
    svc.process_frame(1, 1.0, [DummyItem(0, 0)], [])
    svc.process_frame(2, 1.5, [DummyItem(5, 0)], []) # dist 5m, dt 0.5s -> valid
    svc.process_frame(3, 10.0, [DummyItem(50, 0)], []) # dt 8.5s > 1.0s -> invalid, gap!
    svc.process_frame(4, 10.5, [DummyItem(55, 0)], []) # dist 5m, dt 0.5s -> valid
    
    res = svc.get_summary()
    p1 = res["players"][0]
    
    # Should only count valid distances: 5m + 5m = 10.0m
    assert p1["estimated_distance_m"] == 10.0
    # Valid duration should be 0.5s + 0.5s = 1.0s
    assert p1["tracking_duration"] == 1.0
    assert p1["data_quality"]["tracking_gaps"] == 1
    assert p1["data_quality"]["continuous_segments"] == 2
    
def test_event_deduplication():
    svc = PlayerAnalyticsService(fps=30.0)
    class DummyItem:
        def __init__(self):
            self.class_name = "player"
            self.track_id = 1
            self.team = "TeamA"
            self.pitch_position = {"x": 10, "y": 10}
            
    svc.process_frame(1, 1.0, [DummyItem()], [
        {"id": "ev1", "player": "1", "event_type": "PASS_CANDIDATE"},
        {"id": "ev1", "player": "1", "event_type": "PASS_CANDIDATE"} # Duplicate ID
    ])
    
    res = svc.get_summary()
    p1 = res["players"][0]
    assert p1["passes"] == 1
