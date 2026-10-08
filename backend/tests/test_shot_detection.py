import pytest
from backend.cv.events.shot_detection import ShotDetectionService

class MockTrackedItem:
    def __init__(self, track_id, team, x, y):
        self.track_id = track_id
        self.team = team
        self.mapping_status = "mapped"
        self.pitch_position = {"x": x, "y": y}
        self.class_name = "player"

def test_shot_detection_flow():
    service = ShotDetectionService(max_shot_duration=3.0, min_shot_distance=5.0, deduplication_window=2.0)
    
    # 1. Player A contacts ball in attacking area (team median < 52.5 -> defending left, attacking right)
    p1 = MockTrackedItem(1, "team_a", 75.0, 30.0) # Attacking right (positive X)
    p2 = MockTrackedItem(2, "team_a", 60.0, 30.0)
    p3 = MockTrackedItem(3, "team_a", 65.0, 30.0)
    p4 = MockTrackedItem(4, "team_a", 70.0, 30.0)
    p5 = MockTrackedItem(5, "team_a", 55.0, 30.0)
    
    # Wait, if median is > 52.5, they are defending right, attacking left.
    # To attack right (positive_x), they should defend left (x < 52.5).
    p1 = MockTrackedItem(1, "team_a", 30.0, 30.0) # Attacking right
    p2 = MockTrackedItem(2, "team_a", 20.0, 30.0)
    p3 = MockTrackedItem(3, "team_a", 25.0, 30.0)
    p4 = MockTrackedItem(4, "team_a", 40.0, 30.0)
    p5 = MockTrackedItem(5, "team_a", 45.0, 30.0)
    # Median = 30.0 (< 52.5), so defending left, attacking right (positive_x)
    
    # Now they shoot from attacking half (x > 52.5)
    # Wait! If they are defending left, they must move forward.
    # Shooter is at 60.0 (attacking half)
    p6 = MockTrackedItem(6, "team_a", 60.0, 30.0)
    
    ball_state = {"state": "tracked", "pitch_position": {"x": 60.1, "y": 30.1}}
    contact_event = {"state": "possible", "confidence": 0.8}
    
    events = service.process(
        frame_idx=10, timestamp=1.0, session_id="s1", match_id="m1",
        tracked_items=[p1, p2, p3, p4, p5, p6], ball_state=ball_state, ball_contact_event=contact_event
    )
    
    assert len(events) == 0
    assert service.active_shot is not None
    assert service.active_shot["shooter"]["track_id"] == 6
    assert service.active_shot["attacking_dir"] == "positive_x"
    
    # 2. Ball moves rapidly towards goal (right side, positive X)
    ball_state = {"state": "tracked", "pitch_position": {"x": 80.0, "y": 30.0}}
    contact_event = None
    events = service.process(
        frame_idx=15, timestamp=1.5, session_id="s1", match_id="m1",
        tracked_items=[p1, p2, p3, p4, p5, p6], ball_state=ball_state, ball_contact_event=contact_event
    )
    
    assert len(events) == 1
    ev = events[0]
    assert ev["event_type"] == "SHOT_CANDIDATE"
    assert ev["team"] == "team_a"
    assert ev["player"] == "6"
    assert ev["metadata"]["distance"] > 10.0
    
def test_interception_not_shot():
    service = ShotDetectionService()
    
    p1 = MockTrackedItem(1, "team_a", 10.0, 10.0)
    
    ball_state = {"state": "tracked", "pitch_position": {"x": 10.0, "y": 10.0}}
    contact = {"state": "possible", "confidence": 0.9}
    
    # Ball contacted by player in own half (not attacking area)
    events = service.process(10, 1.0, "s1", "m1", [p1], ball_state, contact)
    assert len(events) == 0
    
    ball_state = {"state": "tracked", "pitch_position": {"x": 20.0, "y": 10.0}}
    events = service.process(20, 2.0, "s1", "m1", [p1], ball_state, None)
    
    assert len(events) == 0 # Not in attacking half, so not a shot candidate
