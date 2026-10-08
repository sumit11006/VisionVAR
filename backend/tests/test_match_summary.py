import pytest
from backend.cv.analytics.match_summary import MatchSummaryService

def test_generate_summary_event_aggregation():
    svc = MatchSummaryService()
    
    events = [
        {"id": "e1", "event_type": "PASS", "player": "1", "metadata": {"state": "confirmed"}},
        {"id": "e2", "event_type": "PASS_CANDIDATE", "player": "2", "metadata": {"state": "uncertain"}},
        {"id": "e3", "event_type": "GOAL", "player": "3", "metadata": {"state": "confirmed"}},
        {"id": "e3", "event_type": "GOAL", "player": "3", "metadata": {"state": "confirmed"}} # Duplicate, should be ignored
    ]
    
    analytics_data = {
        "metadata": {
            "unique_track_ids": 10,
            "total_mapped_samples": 500,
            "known_team_samples_percentage": 80
        },
        "teams": [
            {"team_name": "team_a", "possession_seconds": 60.0},
            {"team_name": "team_b", "possession_seconds": 40.0},
            {"team_name": "unknown", "possession_seconds": 20.0}
        ],
        "players": [
            {"player_id": "1", "estimated_distance_m": 500.0}
        ]
    }
    
    detections_meta = {"processed_frames": 100}
    video_meta = {"total_frames": 100, "duration_seconds": 3.33}
    
    summary = svc.generate_summary(
        session_id="sess_123",
        events=events,
        analytics_data=analytics_data,
        detections_meta=detections_meta,
        video_meta=video_meta
    )
    
    ev_sum = summary["event_summary"]
    assert ev_sum["passes"]["confirmed"] == 1
    assert ev_sum["passes"]["uncertain"] == 1
    assert ev_sum["passes"]["candidate"] == 0
    assert ev_sum["goals"]["confirmed"] == 1  # Deduplicated!
    
    # Check possession aggregation excluding unknown
    # Total valid = 60 + 40 = 100
    assert summary["possession"]["team_a"] == 60.0
    assert summary["possession"]["team_b"] == 40.0
    assert "unknown" not in summary["possession"]
    
    # Check tactical insights
    insights = summary["tactical_insights"]
    assert any("team_a recorded more confirmed possession" in insight for insight in insights)
    assert any("Player Track ID 1 covered the largest estimated distance" in insight for insight in insights)
    
    # Check data quality
    dq = summary["data_quality"]
    assert dq["total_video_frames"] == 100
    assert dq["analyzed_frames"] == 100
    assert dq["unique_track_ids"] == 10
    
def test_empty_match():
    svc = MatchSummaryService()
    summary = svc.generate_summary("sess_123", [], {}, {}, {})
    assert summary["session_id"] == "sess_123"
    assert summary["event_summary"]["goals"]["confirmed"] == 0
    assert len(summary["tactical_insights"]) == 0
