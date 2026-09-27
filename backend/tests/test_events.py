import pytest
from backend.cv.events.service import EventDetectionService

def test_ball_contact_event():
    service = EventDetectionService()
    ball_contact = {"state": "possible", "confidence": 0.8, "evidence": {"reason": "speed spike"}}
    tracked_items = []
    
    events = service.process(10, 0.5, "sess_1", "match_1", tracked_items, None, ball_contact, None)
    
    assert len(events) == 1
    assert events[0]["event_type"] == "BALL_CONTACT"
    assert events[0]["status"] == "candidate"
    assert events[0]["metadata"]["reason"] == "speed spike"

def test_offside_candidate_event():
    service = EventDetectionService()
    offside_data = {"status": "candidate", "ai_assessment": "POTENTIAL OFFSIDE", "evidence": "Geometry matched"}
    
    events = service.process(15, 0.7, "sess_1", "match_1", [], None, None, offside_data)
    
    assert len(events) == 1
    assert events[0]["event_type"] == "OFFSIDE_CANDIDATE"
    assert events[0]["metadata"]["ai_assessment"] == "POTENTIAL OFFSIDE"

def test_possession_and_pass_candidate():
    service = EventDetectionService()
    
    # Mock player 1 from team A
    class MockPlayer:
        def __init__(self, tid, team, px, py):
            self.track_id = tid
            self.team = team
            self.pitch_position = {"x": px, "y": py}
            self.mapping_status = "mapped"
            
    p1 = MockPlayer(1, "team_a", 10, 10)
    p2 = MockPlayer(2, "team_a", 20, 20)
    
    # Frame 1: Ball with p1
    ball = {"state": "tracked", "pitch_position": {"x": 10.1, "y": 10.1}}
    events = service.process(1, 1.0, "sess", "match", [p1, p2], ball, None, None)
    assert len(events) == 0 # initial possession
    
    # Frame 2: Possession held for > 1 sec
    events = service.process(20, 2.5, "sess", "match", [p1, p2], ball, None, None)
    assert len(events) == 1
    assert events[0]["event_type"] == "POSSESSION_CANDIDATE"
    assert events[0]["player"] == "1"
    
    # Frame 3: Ball moves to p2 (Pass candidate)
    ball2 = {"state": "tracked", "pitch_position": {"x": 20.1, "y": 20.1}}
    events = service.process(30, 3.5, "sess", "match", [p1, p2], ball2, None, None)
    
    # Should yield Pass Candidate
    pass_events = [e for e in events if e["event_type"] == "PASS_CANDIDATE"]
    assert len(pass_events) == 1
    assert pass_events[0]["metadata"]["passer_track_id"] == 1
    assert pass_events[0]["metadata"]["receiver_track_id"] == 2

def test_turnover_and_recovery():
    service = EventDetectionService()
    class MockPlayer:
        def __init__(self, tid, team, px, py):
            self.track_id = tid
            self.team = team
            self.pitch_position = {"x": px, "y": py}
            self.mapping_status = "mapped"
            
    p1 = MockPlayer(1, "team_a", 10, 10)
    p3 = MockPlayer(3, "team_b", 40, 40)
    
    ball = {"state": "tracked", "pitch_position": {"x": 10.1, "y": 10.1}}
    service.process(1, 1.0, "s", "m", [p1, p3], ball, None, None)
    
    # Ball moves to team B
    ball2 = {"state": "tracked", "pitch_position": {"x": 40.1, "y": 40.1}}
    events = service.process(10, 2.0, "s", "m", [p1, p3], ball2, None, None)
    
    turnover = [e for e in events if e["event_type"] == "TURNOVER_CANDIDATE"]
    recovery = [e for e in events if e["event_type"] == "BALL_RECOVERY_CANDIDATE"]
    
    assert len(turnover) == 1
    assert turnover[0]["team"] == "team_a"
    assert len(recovery) == 1
    assert recovery[0]["team"] == "team_b"

def test_event_deduplication():
    service = EventDetectionService(deduplication_window=2.0)
    
    ball_contact = {"state": "possible", "confidence": 0.8}
    events1 = service.process(1, 1.0, "s", "m", [], None, ball_contact, None)
    assert len(events1) == 1
    
    # Same event type within 2 seconds
    events2 = service.process(2, 1.5, "s", "m", [], None, ball_contact, None)
    assert len(events2) == 0 # Deduplicated
    
    # After 2 seconds
    events3 = service.process(3, 3.5, "s", "m", [], None, ball_contact, None)
    assert len(events3) == 1
