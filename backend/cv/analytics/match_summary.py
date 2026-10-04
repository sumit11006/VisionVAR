import json
from pathlib import Path
from typing import Dict, Any, List

class MatchSummaryService:
    """
    Creates a match-level intelligence layer aggregating outputs from CV processing.
    """
    def __init__(self):
        pass

    def generate_summary(self, session_id: str, 
                         events: List[Dict[str, Any]], 
                         analytics_data: Dict[str, Any], 
                         detections_meta: Dict[str, Any],
                         video_meta: Dict[str, Any]) -> Dict[str, Any]:
        
        # 1. MATCH EVENT SUMMARY
        event_summary = {
            "goals": {"confirmed": 0, "candidate": 0},
            "shots": {"confirmed": 0, "candidate": 0},
            "passes": {"confirmed": 0, "candidate": 0, "uncertain": 0},
            "turnovers": {"confirmed": 0, "candidate": 0},
            "possession_changes": 0,
            "ball_contacts": 0,
            "offside_candidates": 0,
            "onside_assessments": 0,
            "insufficient_evidence_cases": 0
        }
        
        processed_ev_ids = set()
        for ev in events:
            ev_id = ev.get("id")
            if ev_id:
                if ev_id in processed_ev_ids:
                    continue
                processed_ev_ids.add(ev_id)
                
            evt_type = ev.get("event_type", "")
            state = ev.get("metadata", {}).get("state", "candidate")
            
            if evt_type == "GOAL":
                event_summary["goals"]["confirmed"] += 1
            elif evt_type == "GOAL_CANDIDATE":
                event_summary["goals"]["candidate"] += 1
            elif evt_type == "SHOT":
                event_summary["shots"]["confirmed"] += 1
            elif evt_type == "SHOT_CANDIDATE":
                event_summary["shots"]["candidate"] += 1
            elif evt_type == "PASS":
                event_summary["passes"]["confirmed"] += 1
            elif evt_type == "PASS_CANDIDATE":
                if state == "uncertain":
                    event_summary["passes"]["uncertain"] += 1
                else:
                    event_summary["passes"]["candidate"] += 1
            elif evt_type == "TURNOVER":
                event_summary["turnovers"]["confirmed"] += 1
            elif evt_type == "TURNOVER_CANDIDATE":
                event_summary["turnovers"]["candidate"] += 1
            elif evt_type == "POSSESSION_CHANGE":
                event_summary["possession_changes"] += 1
            elif evt_type == "BALL_CONTACT":
                event_summary["ball_contacts"] += 1
            elif evt_type == "OFFSIDE_CANDIDATE":
                event_summary["offside_candidates"] += 1
            elif evt_type == "ONSIDE_ASSESSMENT":
                event_summary["onside_assessments"] += 1
            elif evt_type == "INSUFFICIENT_EVIDENCE":
                event_summary["insufficient_evidence_cases"] += 1

        # 2. TEAM & POSSESSION SUMMARY
        teams = analytics_data.get("teams", [])
        total_possession_s = sum(t.get("possession_seconds", 0) for t in teams if t.get("team_name") != "unknown")
        
        possession_stats = {}
        for t in teams:
            tname = t.get("team_name")
            poss_s = t.get("possession_seconds", 0)
            if tname != "unknown" and total_possession_s > 0:
                possession_stats[tname] = round((poss_s / total_possession_s) * 100, 1)

        # 3. DATA QUALITY SUMMARY
        meta = analytics_data.get("metadata", {})
        data_quality = {
            "total_video_frames": video_meta.get("total_frames", 0),
            "analyzed_frames": detections_meta.get("processed_frames", 0),
            "mapped_samples": meta.get("total_mapped_samples", 0),
            "unique_track_ids": meta.get("unique_track_ids", 0),
            "known_team_samples_percentage": meta.get("known_team_samples_percentage", 0),
            "insufficient_evidence_events": event_summary["insufficient_evidence_cases"]
        }
        
        # 4. TACTICAL INSIGHTS
        insights = []
        if possession_stats:
            dominant_team = max(possession_stats.items(), key=lambda x: x[1])
            insights.append(f"Team {dominant_team[0]} recorded more confirmed possession duration ({dominant_team[1]}%).")
            
        players = analytics_data.get("players", [])
        if players:
            # Safely filter players who actually have an estimated_distance_m
            valid_runners = [p for p in players if p.get("estimated_distance_m", 0) > 0]
            if valid_runners:
                top_runner = max(valid_runners, key=lambda x: x["estimated_distance_m"])
                insights.append(f"Player Track ID {top_runner['player_id']} covered the largest estimated distance ({top_runner['estimated_distance_m']}m) among sufficiently tracked instances.")
                
        if event_summary["turnovers"]["confirmed"] > 0 or event_summary["turnovers"]["candidate"] > 0:
            team_turnovers = {}
            for t in teams:
                team_turnovers[t["team_name"]] = t.get("turnovers", 0)
            if team_turnovers:
                worst_team = max(team_turnovers.items(), key=lambda x: x[1])
                if worst_team[1] > 0 and worst_team[0] != "unknown":
                    insights.append(f"Team {worst_team[0]} had more observed turnovers ({worst_team[1]}).")

        summary = {
            "session_id": session_id,
            "match_duration_s": video_meta.get("duration_seconds", 0),
            "event_summary": event_summary,
            "possession": possession_stats,
            "team_analytics": teams,
            "player_analytics_summary": {
                "top_runners": [p["player_id"] for p in sorted(players, key=lambda x: x.get("estimated_distance_m", 0), reverse=True)[:3]]
            },
            "formations": [], # Placeholders since we rely on external formation stats currently
            "tactical_insights": insights,
            "data_quality": data_quality
        }
        return summary
