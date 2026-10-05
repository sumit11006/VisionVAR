from typing import Optional, List, Dict, Any
from mcp.server.mcpserver import MCPServer
from pydantic import BaseModel, Field
import json
import os
from pathlib import Path

from backend.app.core.database import SessionLocal
from backend.app.core.config import settings
from backend.app.models.match import Match
from backend.app.models.event import MatchEvent
from backend.app.models.session import AnalysisSession
from backend.app.services.live_runner import active_live_runners

# Initialize MCPServer
mcp = MCPServer("VisionVAR")

def get_db():
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise

@mcp.tool()
def get_match_summary(match_id: str) -> str:
    """
    Get the match summary containing duration, teams, observed possession, passes, shots, goals, and formations.
    """
    db = get_db()
    try:
        match = db.query(Match).filter(Match.id == match_id).first()
        if not match:
            return json.dumps({"error": f"Match {match_id} not found."})

        # Try to read match_summary.json
        summary_path = Path(settings.SESSIONS_DIR) / match_id / "match_summary.json"
        if summary_path.exists():
            with open(summary_path, 'r') as f:
                data = json.load(f)
                return json.dumps(data, indent=2)

        return json.dumps({"error": f"Match summary for {match_id} is unavailable. No analysis.json found."})
    finally:
        db.close()

@mcp.tool()
def get_team_analytics(match_id: str, team_code: str) -> str:
    """
    Get team analytics including observed possession, distance covered, passes, shots, turnovers, and tracked IDs.
    """
    db = get_db()
    try:
        analytics_path = Path(settings.SESSIONS_DIR) / match_id / "analytics.json"
        if not analytics_path.exists():
            return json.dumps({"error": f"Analytics unavailable for {match_id}."})
        
        with open(analytics_path, 'r') as f:
            data = json.load(f)
        
        # We need to find team data. If match_summary exists, it's easier.
        summary_path = Path(settings.SESSIONS_DIR) / match_id / "match_summary.json"
        if summary_path.exists():
            with open(summary_path, 'r') as f:
                summary = json.load(f)
                team_data = summary.get("teams", {}).get(team_code)
                if team_data:
                    return json.dumps(team_data, indent=2)
                    
        return json.dumps({"error": f"Team {team_code} analytics not found in {match_id}."})
    finally:
        db.close()

@mcp.tool()
def get_player_analytics(match_id: str, track_id: str) -> str:
    """
    Get analytics for a specific observed Track ID (team, distance, speed, tracking duration, passes, shots).
    Note: Track IDs are not real player identities.
    """
    try:
        analytics_path = Path(settings.SESSIONS_DIR) / match_id / "analytics.json"
        if not analytics_path.exists():
            return json.dumps({"error": f"Analytics unavailable for {match_id}."})
        
        with open(analytics_path, 'r') as f:
            data = json.load(f)
            
        players = data.get("players", {})
        if track_id in players:
            return json.dumps(players[track_id], indent=2)
        
        return json.dumps({"error": f"Track ID {track_id} not found in {match_id}."})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def get_events(match_id: str, event_type: str = None, status: str = None) -> str:
    """
    Get timeline events like PASS_CANDIDATE, SHOT_CANDIDATE, GOAL, OFFSIDE_CANDIDATE, POSSESSION_CHANGE.
    """
    db = get_db()
    try:
        query = db.query(MatchEvent).filter(MatchEvent.match_id == match_id)
        if event_type:
            query = query.filter(MatchEvent.type == event_type)
        if status:
            query = query.filter(MatchEvent.status == status)
            
        events = query.order_by(MatchEvent.timecode).all()
        results = []
        for e in events:
            results.append({
                "event_type": e.type,
                "frame": e.frame_id,
                "timestamp": e.timecode,
                "status": e.status,
                "confidence": e.confidence,
                "involved_track_ids": [],
                "evidence": e.ai_explanation,
                "metadata": json.loads(e.metadata_json) if e.metadata_json else {}
            })
        return json.dumps({"count": len(results), "events": results}, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})
    finally:
        db.close()

@mcp.tool()
def get_offside_incidents(match_id: str) -> str:
    """
    Get all offside incidents (AI Offside Analysis / Possible Offside) and their evidence.
    """
    db = get_db()
    try:
        events = db.query(MatchEvent).filter(
            MatchEvent.match_id == match_id,
            MatchEvent.type.in_(["OFFSIDE_CANDIDATE", "OFFSIDE", "OFFSIDE_REVIEW"])
        ).order_by(MatchEvent.timecode).all()
        
        results = []
        for e in events:
            meta = json.loads(e.metadata_json) if e.metadata_json else {}
            results.append({
                "frame": e.frame_id,
                "timestamp": e.timecode,
                "status": e.status,
                "ai_assessment": "AI Assessment: " + (e.ai_explanation or "Insufficient Evidence"),
                "attacking_track_id": meta.get("attacker_id"),
                "defending_track_id": meta.get("defender_id"),
                "confidence": e.confidence,
                "evidence": e.ai_explanation
            })
        return json.dumps(results, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})
    finally:
        db.close()

@mcp.tool()
def get_formation(match_id: str, team_code: str = None) -> str:
    """
    Get the observed formation and formation history.
    """
    try:
        summary_path = Path(settings.SESSIONS_DIR) / match_id / "match_summary.json"
        if summary_path.exists():
            with open(summary_path, 'r') as f:
                data = json.load(f)
                
            formations = data.get("formations", {})
            if team_code:
                return json.dumps(formations.get(team_code, {"error": "No formation data for team"}), indent=2)
            return json.dumps(formations, indent=2)
            
        return json.dumps({"error": "No formation data available (insufficient pitch mapping or analysis missing)."})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def get_player_position(match_id: str, track_id: str, frame: int = None) -> str:
    """
    Get specific player image and pitch coordinates at a given frame.
    """
    try:
        analytics_path = Path(settings.SESSIONS_DIR) / match_id / "analytics.json"
        if not analytics_path.exists():
            return json.dumps({"error": "Analytics data missing."})
        
        with open(analytics_path, 'r') as f:
            data = json.load(f)
            
        player = data.get("players", {}).get(track_id)
        if not player:
            return json.dumps({"error": f"Track ID {track_id} not found."})
            
        positions = player.get("positions", [])
        if frame is not None:
            pos = next((p for p in positions if p.get("frame") == frame), None)
            if pos:
                return json.dumps(pos)
            return json.dumps({"error": f"No position data for Track ID {track_id} at frame {frame}."})
            
        return json.dumps({
            "error": "Frame not provided, returning last known position",
            "last_pos": player.get("last_pos") or "Position unavailable due to insufficient pitch mapping evidence."
        })
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def get_live_status(session_id: str) -> str:
    """
    Get the actual status of a live processing session including FPS and latencies.
    """
    if session_id in active_live_runners:
        runner = active_live_runners[session_id]
        import time
        fps = runner.processed_count / max(0.1, time.time() - runner.start_time)
        return json.dumps({
            "status": "RUNNING",
            "source": runner.video_source,
            "processed_fps": fps,
            "current_frame": runner.processed_count,
            "tracked_objects": len(runner.tracker.tracked_items) if hasattr(runner.tracker, 'tracked_items') else 0
        }, indent=2)
        
    db = get_db()
    try:
        session = db.query(AnalysisSession).filter(AnalysisSession.id == session_id).first()
        if session:
            return json.dumps({"status": session.status, "message": "Live session not actively running in memory."})
        return json.dumps({"error": f"Session {session_id} not found."})
    finally:
        db.close()

@mcp.tool()
def get_video_frame(session_id_or_match_id: str, frame_number: int) -> str:
    """
    Get frame metadata. Actual image retrieval is unavailable through MCP.
    """
    return json.dumps({
        "frame_number": frame_number,
        "status": "Metadata only. Image retrieval is unavailable through MCP interface.",
        "session_or_match_id": session_id_or_match_id
    })

