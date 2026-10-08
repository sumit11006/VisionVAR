import pytest
from backend.cv.events.possession import PossessionService

def test_possession_established():
    svc = PossessionService(distance_threshold_m=2.0, firm_possession_frames=3)
    
    # 3 frames of player 1 holding ball
    for i in range(1, 4):
        class DummyItem:
            pass
        t_obj = DummyItem()
        setattr(t_obj, "class_name", "player")
        setattr(t_obj, "track_id", 1)
        setattr(t_obj, "team", "team_a")
        setattr(t_obj, "pitch_position", {"x": 50, "y": 30})
        
        ball = {"state": "tracked", "pitch_position": {"x": 50.5, "y": 30.5}}
        events = svc.process(i, float(i), [t_obj], ball, ball_contact_event=None)
        
        if i < 3:
            assert len(events) == 0
        else:
            assert len(events) == 1
            assert events[0]["event_type"] == "POSSESSION_CHANGE"
            assert events[0]["player"] == "1"
            assert events[0]["team"] == "team_a"

def test_turnover_detection():
    svc = PossessionService(distance_threshold_m=2.0, firm_possession_frames=2)
    
    class DummyItem: pass

    # Player 1 (team_a) has it
    for i in range(1, 3):
        t_obj = DummyItem()
        setattr(t_obj, "class_name", "player")
        setattr(t_obj, "track_id", 1)
        setattr(t_obj, "team", "team_a")
        setattr(t_obj, "pitch_position", {"x": 50, "y": 30})
        ball = {"state": "tracked", "pitch_position": {"x": 50, "y": 30}}
        svc.process(i, float(i), [t_obj], ball, ball_contact_event=None)

    # Player 2 (team_b) takes it for 2 frames
    for i in range(3, 5):
        t_obj = DummyItem()
        setattr(t_obj, "class_name", "player")
        setattr(t_obj, "track_id", 2)
        setattr(t_obj, "team", "team_b")
        setattr(t_obj, "pitch_position", {"x": 55, "y": 30})
        ball = {"state": "tracked", "pitch_position": {"x": 55, "y": 30}}
        events = svc.process(i, float(i), [t_obj], ball, ball_contact_event=None)
        if i == 4:
            assert len(events) == 1
            assert events[0]["event_type"] == "TURNOVER_CANDIDATE"
            assert events[0]["team"] == "team_b"

def test_short_touch():
    svc = PossessionService(distance_threshold_m=2.0, firm_possession_frames=5, short_touch_min_frames=1, short_touch_max_frames=3)
    
    class DummyItem: pass
    
    # P1 (team_a) has firm possession
    for i in range(1, 6):
        t_obj = DummyItem()
        setattr(t_obj, "class_name", "player")
        setattr(t_obj, "track_id", 1)
        setattr(t_obj, "team", "team_a")
        setattr(t_obj, "pitch_position", {"x": 50, "y": 30})
        ball = {"state": "tracked", "pitch_position": {"x": 50, "y": 30}}
        svc.process(i, float(i), [t_obj], ball, ball_contact_event=None)
        
    assert svc.last_known_possessor == 1
        
    # P2 (team_a) touches it for just 2 frames with ball contact
    for i in range(6, 8):
        t_obj = DummyItem()
        setattr(t_obj, "class_name", "player")
        setattr(t_obj, "track_id", 2)
        setattr(t_obj, "team", "team_a")
        setattr(t_obj, "pitch_position", {"x": 60, "y": 30})
        ball = {"state": "tracked", "pitch_position": {"x": 60, "y": 30}}
        contact = {"state": "possible"}
        events = svc.process(i, float(i), [t_obj], ball, ball_contact_event=contact)
        assert len(events) == 0  # not firm possession yet
        
    # Ball leaves P2, dist > 2.0
    t_obj = DummyItem()
    setattr(t_obj, "class_name", "player")
    setattr(t_obj, "track_id", 2)
    setattr(t_obj, "team", "team_a")
    setattr(t_obj, "pitch_position", {"x": 60, "y": 30})
    ball = {"state": "tracked", "pitch_position": {"x": 80, "y": 30}} # ball 20m away
    events = svc.process(8, 8.0, [t_obj], ball, ball_contact_event=None)
    
    # We should get a SHORT_TOUCH_POSSESSION event
    assert len(events) == 1
    assert events[0]["event_type"] == "SHORT_TOUCH_POSSESSION"
    assert events[0]["player"] == "2"

def test_false_short_touch():
    svc = PossessionService(distance_threshold_m=2.0, firm_possession_frames=5)
    
    class DummyItem: pass
    
    # P1 (team_a) has firm possession
    for i in range(1, 6):
        t_obj = DummyItem()
        setattr(t_obj, "class_name", "player")
        setattr(t_obj, "track_id", 1)
        setattr(t_obj, "team", "team_a")
        setattr(t_obj, "pitch_position", {"x": 50, "y": 30})
        ball = {"state": "tracked", "pitch_position": {"x": 50, "y": 30}}
        svc.process(i, float(i), [t_obj], ball, ball_contact_event=None)
        
    # P2 (team_b) is near the ball for 2 frames BUT no ball contact
    for i in range(6, 8):
        t_obj = DummyItem()
        setattr(t_obj, "class_name", "player")
        setattr(t_obj, "track_id", 2)
        setattr(t_obj, "team", "team_b")
        setattr(t_obj, "pitch_position", {"x": 60, "y": 30})
        ball = {"state": "tracked", "pitch_position": {"x": 60, "y": 30}}
        events = svc.process(i, float(i), [t_obj], ball, ball_contact_event=None)
        
    # Ball leaves P2
    ball = {"state": "tracked", "pitch_position": {"x": 80, "y": 30}}
    events = svc.process(8, 8.0, [t_obj], ball, ball_contact_event=None)
    
    # Should be NO event because there was no contact evidence
    assert len(events) == 0
