import pytest
from backend.cv.events.ball_contact import BallContactService
from backend.cv.offside.service import OffsideAnalysisService

def test_ball_contact_uncertain():
    service = BallContactService()
    res = service.process_frame(None, 1, 0.0)
    assert res["state"] == "uncertain"
    assert res["confidence"] == 0.0

def test_ball_contact_reacquired():
    service = BallContactService()
    # Frame 1: Lost
    service.process_frame({"state": "lost"}, 1, 0.0)
    # Frame 2: Reacquired
    res = service.process_frame({"state": "reacquired", "pitch_position": {"x": 50, "y": 34}}, 2, 0.1)
    assert res["state"] == "possible"
    assert res["evidence"]["reason"] == "reacquired"

def test_offside_insufficient_defenders():
    offside_service = OffsideAnalysisService()
    tracked_items = [
        {"class_name": "player", "mapping_status": "mapped", "team": "team_a", "track_id": 1, "pitch_position": {"x": 80, "y": 30}},
        {"class_name": "player", "mapping_status": "mapped", "team": "team_b", "track_id": 2, "pitch_position": {"x": 70, "y": 30}},
    ]
    
    # Needs at least 5 players to determine attacking direction, so it will be unknown
    ball_contact = {"state": "possible"}
    res = offside_service.analyze(ball_contact, tracked_items, 0.0, 1)
    
    assert res["team_a_attacking_dir"] == "unknown"
    assert res["team_b_attacking_dir"] == "unknown"
    assert res["offside_line_against_a"]["status"] == "unavailable"

def test_offside_geometry():
    offside_service = OffsideAnalysisService()
    # Setup 5 players for team B to establish median > 52.5 (defending right -> attacking left)
    tracked_items = [
        # Team A (Attacking Right -> positive_x) -> needs median < 52.5
        {"class_name": "player", "mapping_status": "mapped", "team": "team_a", "track_id": 1, "pitch_position": {"x": 10, "y": 10}},
        {"class_name": "player", "mapping_status": "mapped", "team": "team_a", "track_id": 2, "pitch_position": {"x": 20, "y": 10}},
        {"class_name": "player", "mapping_status": "mapped", "team": "team_a", "track_id": 3, "pitch_position": {"x": 30, "y": 10}},
        {"class_name": "player", "mapping_status": "mapped", "team": "team_a", "track_id": 4, "pitch_position": {"x": 40, "y": 10}},
        {"class_name": "player", "mapping_status": "mapped", "team": "team_a", "track_id": 5, "pitch_position": {"x": 80, "y": 10}}, # Offside attacker
        
        # Team B (Defending Right) -> median > 52.5
        {"class_name": "player", "mapping_status": "mapped", "team": "team_b", "track_id": 6, "pitch_position": {"x": 90, "y": 10}}, # GK
        {"class_name": "player", "mapping_status": "mapped", "team": "team_b", "track_id": 7, "pitch_position": {"x": 75, "y": 10}}, # 2nd last def
        {"class_name": "player", "mapping_status": "mapped", "team": "team_b", "track_id": 8, "pitch_position": {"x": 70, "y": 10}},
        {"class_name": "player", "mapping_status": "mapped", "team": "team_b", "track_id": 9, "pitch_position": {"x": 60, "y": 10}},
        {"class_name": "player", "mapping_status": "mapped", "team": "team_b", "track_id": 10, "pitch_position": {"x": 60, "y": 10}},
    ]
    
    res = offside_service.analyze({"state": "possible"}, tracked_items, 0.0, 1)
    
    assert res["team_a_attacking_dir"] == "positive_x"
    assert res["offside_line_against_a"]["status"] == "available"
    assert res["offside_line_against_a"]["x"] == 75.0
    assert res["offside_line_against_a"]["defender_id"] == 7
    
    # Attacker 5 at x=80 should be offside since 80 > 75 and attacking right
    attacker_status = next(p["status"] for p in res["players"] if p["track_id"] == 5)
    assert attacker_status == "potentially_offside"
    
    # Attacker 4 at x=40 should be onside
    attacker2_status = next(p["status"] for p in res["players"] if p["track_id"] == 4)
    assert attacker2_status == "onside"
    
    assert res["ai_assessment"] == "POTENTIAL OFFSIDE"
    assert res["evidence"] == "SUFFICIENT FOR GEOMETRIC REVIEW"

def test_offside_insufficient_evidence():
    offside_service = OffsideAnalysisService()
    tracked_items = [
        {"class_name": "player", "mapping_status": "mapped", "team": "team_a", "track_id": 1, "pitch_position": {"x": 80, "y": 30}},
        {"class_name": "player", "mapping_status": "mapped", "team": "team_b", "track_id": 2, "pitch_position": {"x": 70, "y": 30}},
    ]
    ball_contact = {"state": "possible"}
    res = offside_service.analyze(ball_contact, tracked_items, 0.0, 1)
    
    assert res["ai_assessment"] == "INSUFFICIENT EVIDENCE"
    assert res["evidence"] == "INSUFFICIENT EVIDENCE"
