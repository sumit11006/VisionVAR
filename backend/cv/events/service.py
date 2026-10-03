import uuid
from typing import List, Dict, Any, Optional

class EventDetectionService:
    def __init__(self, deduplication_window: float = 2.0):
        self.deduplication_window = deduplication_window
        self.last_events = {}  # type_key -> {"timestamp": float, "event": dict}
        
        # State for heuristics
        self.current_possessor = None
        self.possession_start_time = 0
        self.last_contact_player = None
        self.last_contact_time = 0
        self.last_ball_contact_event_time = 0

    def process(
        self,
        frame_idx: int,
        timestamp: float,
        session_id: str,
        match_id: str,
        tracked_items: List[Any],
        ball_state: Optional[Dict[str, Any]],
        ball_contact_event: Optional[Dict[str, Any]],
        offside_candidate: Optional[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        events = []
        
        nearest_player = self._get_nearest_player(ball_state, tracked_items)
        
        # 1. BALL_CONTACT
        if ball_contact_event and ball_contact_event.get("state") == "possible":
            self.last_ball_contact_event_time = timestamp
            if nearest_player:
                self.last_contact_player = {
                    "track_id": nearest_player.track_id,
                    "team": getattr(nearest_player, "team", "unknown")
                }
                self.last_contact_time = timestamp
                
            evidence = ball_contact_event.get("evidence", {})
            events.append({
                "id": str(uuid.uuid4()),
                "match_id": match_id,
                "session_id": session_id,
                "event_type": "BALL_CONTACT",
                "timestamp": timestamp,
                "frame": frame_idx,
                "status": "candidate",
                "confidence": ball_contact_event.get("confidence", 0.0),
                "team": getattr(nearest_player, "team", "unknown") if nearest_player else "unknown",
                "player": str(nearest_player.track_id) if nearest_player else None,
                "metadata": evidence
            })
            
        # 2. OFFSIDE_CANDIDATE
        if offside_candidate and offside_candidate.get("status") == "candidate":
            ai_assessment = offside_candidate.get("ai_assessment")
            if ai_assessment == "POTENTIAL OFFSIDE":
                events.append({
                    "id": str(uuid.uuid4()),
                    "match_id": match_id,
                    "session_id": session_id,
                    "event_type": "OFFSIDE_CANDIDATE",
                    "timestamp": timestamp,
                    "frame": frame_idx,
                    "status": "candidate",
                    "confidence": 0.8,
                    "team": "unknown",
                    "player": None,
                    "metadata": {
                        "evidence": offside_candidate.get("evidence"),
                        "ai_assessment": ai_assessment
                    }
                })
                
        # Possession Tracking
        if nearest_player:
            player_info = {
                "track_id": nearest_player.track_id,
                "team": getattr(nearest_player, "team", "unknown")
            }
            if not self.current_possessor:
                self.current_possessor = player_info
                self.possession_start_time = timestamp
            elif self.current_possessor["track_id"] != player_info["track_id"]:
                # Potential transition
                prev_possessor = self.current_possessor
                self.current_possessor = player_info
                self.possession_start_time = timestamp
                
                # Check for RECOVERY / TURNOVER
                if prev_possessor["team"] != "unknown" and player_info["team"] != "unknown" and prev_possessor["team"] != player_info["team"]:
                    # Turnover / Recovery
                    events.append({
                        "id": str(uuid.uuid4()),
                        "match_id": match_id,
                        "session_id": session_id,
                        "event_type": "TURNOVER_CANDIDATE",
                        "timestamp": timestamp,
                        "frame": frame_idx,
                        "status": "candidate",
                        "confidence": 0.7,
                        "team": prev_possessor["team"],
                        "player": str(prev_possessor["track_id"]),
                        "metadata": {
                            "lost_by": prev_possessor["track_id"],
                            "recovered_by": player_info["track_id"]
                        }
                    })
                    events.append({
                        "id": str(uuid.uuid4()),
                        "match_id": match_id,
                        "session_id": session_id,
                        "event_type": "BALL_RECOVERY_CANDIDATE",
                        "timestamp": timestamp,
                        "frame": frame_idx,
                        "status": "candidate",
                        "confidence": 0.7,
                        "team": player_info["team"],
                        "player": str(player_info["track_id"]),
                        "metadata": {
                            "recovered_by": player_info["track_id"]
                        }
                    })
        
        # POSSESSION_CANDIDATE
        if self.current_possessor and (timestamp - self.possession_start_time) > 1.0: # Held for > 1 second
            events.append({
                "id": str(uuid.uuid4()),
                "match_id": match_id,
                "session_id": session_id,
                "event_type": "POSSESSION_CANDIDATE",
                "timestamp": timestamp,
                "frame": frame_idx,
                "status": "candidate",
                "confidence": 0.5,
                "team": self.current_possessor["team"],
                "player": str(self.current_possessor["track_id"]),
                "metadata": {
                    "duration": timestamp - self.possession_start_time
                }
            })
                
        return self._deduplicate(events, timestamp)

    def _get_nearest_player(self, ball_state, tracked_items):
        if not ball_state or ball_state.get("state") not in ["tracked", "reacquired"] or not ball_state.get("pitch_position"):
            return None
            
        ball_pos = ball_state["pitch_position"]
        bx, by = ball_pos["x"], ball_pos["y"]
        
        min_dist = float('inf')
        nearest = None
        
        for p in tracked_items:
            if getattr(p, "mapping_status", "") == "mapped" and hasattr(p, "pitch_position") and p.pitch_position:
                px, py = p.pitch_position["x"], p.pitch_position["y"]
                dist = ((bx - px)**2 + (by - py)**2)**0.5
                if dist < min_dist:
                    min_dist = dist
                    nearest = p
                    
        if min_dist < 3.0:
            return nearest
        return None

    def _deduplicate(self, new_events, current_timestamp):
        emitted_events = []
        for e in new_events:
            ev_type = e["event_type"]
            
            # Use team/player in deduplication key if they exist
            dedup_key = f"{ev_type}_{e.get('team')}_{e.get('player')}"
            
            last = self.last_events.get(dedup_key)
            
            if not last or (current_timestamp - last["timestamp"] > self.deduplication_window):
                emitted_events.append(e)
                self.last_events[dedup_key] = {"timestamp": current_timestamp, "event": e}
                
        return emitted_events
