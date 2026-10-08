import pytest
from backend.cv.events.pass_detection import PassDetectionService

class MockTrackedItem:
    def __init__(self, track_id, team, x, y):
        self.track_id = track_id
        self.team = team
        self.mapping_status = "mapped"
        self.pitch_position = {"x": x, "y": y}
        self.class_name = "player"

def test_pass_detection_flow():
    service = PassDetectionService(max_pass_duration=5.0, min_pass_distance=2.0, deduplication_window=2.0)
    
    # 1. Player A contacts ball
    p1 = MockTrackedItem(1, "team_a", 10.0, 10.0)
    p2 = MockTrackedItem(2, "team_a", 20.0, 10.0)
    
    ball_state = {"state": "tracked", "pitch_position": {"x": 10.1, "y": 10.1}}
    contact_event = {"state": "possible", "confidence": 0.8}
    
    events = service.process(
        frame_idx=10, timestamp=1.0, session_id="s1", match_id="m1",
        tracked_items=[p1, p2], ball_state=ball_state, ball_contact_event=contact_event
    )
    
    # No event yet, just active pass started
    assert len(events) == 0
    assert service.active_pass is not None
    assert service.active_pass["passer"]["track_id"] == 1
    
    # 2. Ball moves
    ball_state = {"state": "tracked", "pitch_position": {"x": 15.0, "y": 10.0}}
    contact_event = None
    events = service.process(
        frame_idx=15, timestamp=1.5, session_id="s1", match_id="m1",
        tracked_items=[p1, p2], ball_state=ball_state, ball_contact_event=contact_event
    )
    assert len(events) == 0
    
    # 3. Player B contacts ball (receives pass)
    ball_state = {"state": "tracked", "pitch_position": {"x": 19.9, "y": 10.1}}
    contact_event = {"state": "possible", "confidence": 0.8}
    events = service.process(
        frame_idx=20, timestamp=2.0, session_id="s1", match_id="m1",
        tracked_items=[p1, p2], ball_state=ball_state, ball_contact_event=contact_event
    )
    
    assert len(events) == 1
    ev = events[0]
    assert ev["event_type"] == "PASS_CANDIDATE"
    assert ev["team"] == "team_a"
    assert ev["player"] == "1"
    assert ev["metadata"]["receiver_track_id"] == 2
    assert ev["metadata"]["distance"] > 9.0
    
def test_interception_flow():
    service = PassDetectionService()
    
    p1 = MockTrackedItem(1, "team_a", 10.0, 10.0)
    p3 = MockTrackedItem(3, "team_b", 20.0, 10.0)
    
    ball_state = {"state": "tracked", "pitch_position": {"x": 10.0, "y": 10.0}}
    contact = {"state": "possible", "confidence": 0.9}
    
    service.process(10, 1.0, "s1", "m1", [p1, p3], ball_state, contact)
    
    # Intercepted by team_b
    ball_state = {"state": "tracked", "pitch_position": {"x": 20.0, "y": 10.0}}
    contact = {"state": "possible", "confidence": 0.9}
    events = service.process(20, 2.0, "s1", "m1", [p1, p3], ball_state, contact)
    
    assert len(events) == 0
    assert service.active_pass["passer"]["track_id"] == 3
    assert service.active_pass["passer"]["team"] == "team_b"
