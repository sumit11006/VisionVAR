import pytest
from backend.cv.field.goal_geometry import GoalGeometry
from backend.cv.events.goal_detection import GoalDetectionService

def test_goal_geometry():
    geom = GoalGeometry(pitch_length=105.0, pitch_width=68.0, goal_width=7.32, y_tolerance=1.0)
    
    assert geom.get_goal_line("positive_x") == 105.0
    assert geom.get_goal_line("negative_x") == 0.0
    assert geom.get_goal_line("unknown") == -1.0
    
    # Center y = 34.0. Goal mouth = [29.34, 38.66] approx.
    assert geom.is_in_goal_mouth(34.0)
    assert geom.is_in_goal_mouth(30.0)
    assert geom.is_in_goal_mouth(38.0)
    
    # Outside goal mouth
    assert not geom.is_in_goal_mouth(25.0)
    assert not geom.is_in_goal_mouth(45.0)
    
    # Did cross line? (positive_x)
    assert geom.did_cross_line(104.0, 105.5, "positive_x")
    assert not geom.did_cross_line(104.0, 104.8, "positive_x")
    
    # Did cross line? (negative_x)
    assert geom.did_cross_line(1.0, -0.5, "negative_x")
    assert not geom.did_cross_line(-0.5, -1.0, "negative_x")
    assert not geom.did_cross_line(1.0, 0.5, "negative_x")

def test_goal_detection_service_positive_x():
    service = GoalDetectionService(deduplication_window=5.0)
    
    # Frame 1: Ball just before goal line
    ball_state1 = {"state": "tracked", "pitch_position": {"x": 104.0, "y": 34.0}}
    events = service.process(1, 1.0, "s1", "m1", ball_state1, {"team_a": "positive_x", "team_b": "negative_x"})
    assert len(events) == 0
    
    # Frame 2: Ball crosses goal line inside goal mouth
    ball_state2 = {"state": "tracked", "pitch_position": {"x": 105.5, "y": 34.5}}
    events = service.process(2, 1.1, "s1", "m1", ball_state2, {"team_a": "positive_x", "team_b": "negative_x"})
    
    assert len(events) == 1
    ev = events[0]
    assert ev["event_type"] == "GOAL_CANDIDATE"
    assert ev["team"] == "team_a"
    assert ev["metadata"]["goal_side"] == "positive_x"
    assert ev["confidence"] >= 0.8
    
    # Frame 3: Ball still past goal line (deduplication check)
    ball_state3 = {"state": "tracked", "pitch_position": {"x": 106.0, "y": 34.5}}
    events = service.process(3, 1.2, "s1", "m1", ball_state3, {"team_a": "positive_x", "team_b": "negative_x"})
    assert len(events) == 0

def test_goal_detection_service_outside_goal_mouth():
    service = GoalDetectionService()
    
    ball_state1 = {"state": "tracked", "pitch_position": {"x": 104.0, "y": 10.0}}
    events = service.process(1, 1.0, "s1", "m1", ball_state1, {"team_a": "positive_x"})
    assert len(events) == 0
    
    # Crosses goal line, but Y=10.0 is way outside the goal mouth
    ball_state2 = {"state": "tracked", "pitch_position": {"x": 106.0, "y": 10.0}}
    events = service.process(2, 1.1, "s1", "m1", ball_state2, {"team_a": "positive_x"})
    
    assert len(events) == 0

def test_goal_detection_service_negative_x():
    service = GoalDetectionService()
    
    ball_state1 = {"state": "tracked", "pitch_position": {"x": 1.0, "y": 34.0}}
    events = service.process(1, 1.0, "s1", "m1", ball_state1, {"team_b": "negative_x"})
    assert len(events) == 0
    
    ball_state2 = {"state": "tracked", "pitch_position": {"x": -1.0, "y": 34.0}}
    events = service.process(2, 1.1, "s1", "m1", ball_state2, {"team_b": "negative_x"})
    
    assert len(events) == 1
    assert events[0]["team"] == "team_b"

def test_goal_detection_missing_ball():
    service = GoalDetectionService()
    
    ball_state1 = {"state": "tracked", "pitch_position": {"x": 104.0, "y": 34.0}}
    events = service.process(1, 1.0, "s1", "m1", ball_state1, {"team_a": "positive_x"})
    assert len(events) == 0
    
    # Ball lost
    ball_state2 = {"state": "lost"}
    events = service.process(2, 1.1, "s1", "m1", ball_state2, {"team_a": "positive_x"})
    assert len(events) == 0
    
    # Ball reacquired across line but 5 seconds later
    ball_state3 = {"state": "tracked", "pitch_position": {"x": 106.0, "y": 34.0}}
    events = service.process(3, 6.1, "s1", "m1", ball_state3, {"team_a": "positive_x"})
    # Time gap > 2.0s -> tracking discontinuous, do not interpolate crossing
    assert len(events) == 0
