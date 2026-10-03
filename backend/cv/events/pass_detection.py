import uuid
import math
from typing import List, Dict, Any, Optional

class PassDetectionService:
    def __init__(self, max_pass_duration: float = 5.0, min_pass_distance: float = 2.0, deduplication_window: float = 2.0):
        self.max_pass_duration = max_pass_duration
        self.min_pass_distance = min_pass_distance
        self.deduplication_window = deduplication_window
        
        self.active_pass = None
        self.last_emitted_pass = None  # For deduplication

    def process(
        self,
        frame_idx: int,
        timestamp: float,
        session_id: str,
        match_id: str,
        tracked_items: List[Any],
        ball_state: Optional[Dict[str, Any]],
        ball_contact_event: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        events = []
        
        nearest_player = self._get_nearest_player(ball_state, tracked_items)
        ball_pos = ball_state.get("pitch_position") if ball_state else None
        
        if self.active_pass and ball_state:
            # Check for disappearance
            if ball_state.get("state") == "lost":
                if timestamp - ball_state.get("last_seen_time", timestamp) > 1.0:
                    self.active_pass = None
            elif timestamp - self.active_pass["start_timestamp"] > self.max_pass_duration:
                self.active_pass = None

        if ball_contact_event and ball_contact_event.get("state") == "possible" and nearest_player and ball_pos:
            contactor = {
                "track_id": nearest_player.track_id,
                "team": getattr(nearest_player, "team", "unknown"),
                "pitch_position": {"x": nearest_player.pitch_position["x"], "y": nearest_player.pitch_position["y"]} if getattr(nearest_player, "pitch_position", None) else ball_pos
            }
            
            contact_conf = ball_contact_event.get("confidence", 0.0)

            if self.active_pass:
                if self.active_pass["passer"]["track_id"] != contactor["track_id"]:
                    # Potential receive!
                    start_pos = self.active_pass["start_pos"]
                    end_pos = contactor["pitch_position"]
                    
                    dist = 0.0
                    if start_pos and end_pos:
                        dist = math.hypot(end_pos["x"] - start_pos["x"], end_pos["y"] - start_pos["y"])
                        
                    # Same team validation
                    team_a = self.active_pass["passer"]["team"]
                    team_b = contactor["team"]
                    
                    status = "candidate"
                    confidence = 0.5 + (contact_conf * 0.2) + (self.active_pass["contact_conf"] * 0.2)
                    
                    if team_a == "unknown" or team_b == "unknown":
                        status = "uncertain"
                        confidence -= 0.2
                    elif team_a != team_b:
                        # Interception, not a pass
                        self.active_pass = {
                            "passer": contactor,
                            "start_pos": contactor["pitch_position"],
                            "start_timestamp": timestamp,
                            "contact_conf": contact_conf
                        }
                        return events
                        
                    # Distance check
                    if dist < self.min_pass_distance:
                        # Too short, probably a scramble or dribble error
                        self.active_pass = {
                            "passer": contactor,
                            "start_pos": contactor["pitch_position"],
                            "start_timestamp": timestamp,
                            "contact_conf": contact_conf
                        }
                        return events
                        
                    # Build PASS event
                    pass_event = {
                        "id": str(uuid.uuid4()),
                        "match_id": match_id,
                        "session_id": session_id,
                        "event_type": "PASS_CANDIDATE",
                        "timestamp": timestamp,
                        "frame": frame_idx,
                        "status": status,
                        "confidence": min(0.99, max(0.1, confidence)),
                        "team": team_a,
                        "player": str(self.active_pass["passer"]["track_id"]),
                        "metadata": {
                            "passer_track_id": self.active_pass["passer"]["track_id"],
                            "receiver_track_id": contactor["track_id"],
                            "start": start_pos,
                            "end": end_pos,
                            "distance": round(dist, 2)
                        }
                    }
                    
                    # Deduplication
                    if not self.last_emitted_pass or \
                       (timestamp - self.last_emitted_pass["timestamp"] > self.deduplication_window) or \
                       (self.last_emitted_pass["metadata"]["passer_track_id"] != pass_event["metadata"]["passer_track_id"]) or \
                       (self.last_emitted_pass["metadata"]["receiver_track_id"] != pass_event["metadata"]["receiver_track_id"]):
                        events.append(pass_event)
                        self.last_emitted_pass = pass_event
                        
                    # Reset active pass to the receiver (they are now the possessor)
                    self.active_pass = {
                        "passer": contactor,
                        "start_pos": contactor["pitch_position"],
                        "start_timestamp": timestamp,
                        "contact_conf": contact_conf
                    }
                else:
                    # Same player contact (dribble), update start pos/time
                    self.active_pass["start_pos"] = contactor["pitch_position"]
                    self.active_pass["start_timestamp"] = timestamp
                    self.active_pass["contact_conf"] = contact_conf
            else:
                self.active_pass = {
                    "passer": contactor,
                    "start_pos": contactor["pitch_position"],
                    "start_timestamp": timestamp,
                    "contact_conf": contact_conf
                }

        return events

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
