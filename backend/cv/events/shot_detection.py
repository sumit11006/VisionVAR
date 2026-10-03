import uuid
import math
import numpy as np
from typing import List, Dict, Any, Optional

class ShotDetectionService:
    def __init__(self, max_shot_duration: float = 3.0, min_shot_distance: float = 5.0, deduplication_window: float = 3.0):
        self.max_shot_duration = max_shot_duration
        self.min_shot_distance = min_shot_distance
        self.deduplication_window = deduplication_window
        
        self.active_shot = None
        self.last_emitted_shot = None

    def determine_attacking_direction(self, team: str, tracked_items: List[Any]) -> str:
        team_x = []
        for p in tracked_items:
            is_dict = isinstance(p, dict)
            class_name = p.get("class_name") if is_dict else getattr(p, "class_name", None)
            mapping_status = p.get("mapping_status") if is_dict else getattr(p, "mapping_status", None)
            p_team = p.get("team") if is_dict else getattr(p, "team", None)
            
            if class_name == "player" and mapping_status == "mapped" and p_team == team:
                pos = p.get("pitch_position") if is_dict else getattr(p, "pitch_position", None)
                if pos:
                    team_x.append(pos["x"])
        
        if len(team_x) < 4:
            return "unknown"
            
        median_x = np.median(team_x)
        if median_x < 52.5: # Defending left, attacking right
            return "positive_x"
        else: # Defending right, attacking left
            return "negative_x"

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
        
        # Check if active shot is progressing or expired
        if self.active_shot and ball_state:
            # If ball lost for > 1.0s, we might invalidate or finalize
            if ball_state.get("state") == "lost":
                if timestamp - ball_state.get("last_seen_time", timestamp) > 1.0:
                    self.active_shot = None
            else:
                elapsed_time = timestamp - self.active_shot["start_timestamp"]
                if elapsed_time > self.max_shot_duration:
                    self.active_shot = None
                elif ball_pos:
                    # Evaluate trajectory
                    start_pos = self.active_shot["start_pos"]
                    dist = math.hypot(ball_pos["x"] - start_pos["x"], ball_pos["y"] - start_pos["y"])
                    
                    if dist >= self.min_shot_distance:
                        # Validate direction
                        dx = ball_pos["x"] - start_pos["x"]
                        attacking_dir = self.active_shot["attacking_dir"]
                        
                        is_towards_goal = False
                        if attacking_dir == "positive_x" and dx > 0:
                            is_towards_goal = True
                        elif attacking_dir == "negative_x" and dx < 0:
                            is_towards_goal = True
                            
                        # If ball is moving toward goal and shooter was in attacking half
                        is_attacking_half = False
                        if attacking_dir == "positive_x" and start_pos["x"] > 52.5:
                            is_attacking_half = True
                        elif attacking_dir == "negative_x" and start_pos["x"] < 52.5:
                            is_attacking_half = True
                            
                        if is_towards_goal and is_attacking_half:
                            contact_conf = self.active_shot["contact_conf"]
                            confidence = 0.6 + (contact_conf * 0.3)
                            
                            status = "candidate"
                            if attacking_dir == "unknown" or self.active_shot["shooter"]["team"] == "unknown":
                                status = "uncertain"
                                confidence -= 0.2
                                
                            shot_event = {
                                "id": str(uuid.uuid4()),
                                "match_id": match_id,
                                "session_id": session_id,
                                "event_type": "SHOT_CANDIDATE",
                                "timestamp": timestamp,
                                "frame": frame_idx,
                                "status": status,
                                "confidence": min(0.99, max(0.1, confidence)),
                                "team": self.active_shot["shooter"]["team"],
                                "player": str(self.active_shot["shooter"]["track_id"]) if self.active_shot["shooter"]["track_id"] else "UNKNOWN",
                                "metadata": {
                                    "shooter_track_id": self.active_shot["shooter"]["track_id"],
                                    "start": start_pos,
                                    "end": ball_pos,
                                    "distance": round(dist, 2),
                                    "attacking_dir": attacking_dir
                                }
                            }
                            
                            # Deduplication
                            if not self.last_emitted_shot or \
                               (timestamp - self.last_emitted_shot["timestamp"] > self.deduplication_window) or \
                               (self.last_emitted_shot["metadata"]["shooter_track_id"] != shot_event["metadata"]["shooter_track_id"]):
                                events.append(shot_event)
                                self.last_emitted_shot = shot_event
                                
                            self.active_shot = None # Done with this shot

        # Start a new active shot candidate on ball contact
        if ball_contact_event and ball_contact_event.get("state") == "possible" and ball_pos:
            shooter = {"track_id": None, "team": "unknown", "pitch_position": ball_pos}
            
            if nearest_player:
                is_dict = isinstance(nearest_player, dict)
                shooter["track_id"] = nearest_player.get("track_id") if is_dict else getattr(nearest_player, "track_id", None)
                shooter["team"] = nearest_player.get("team") if is_dict else getattr(nearest_player, "team", "unknown")
                p_pos = nearest_player.get("pitch_position") if is_dict else getattr(nearest_player, "pitch_position", None)
                if p_pos:
                    shooter["pitch_position"] = {"x": p_pos["x"], "y": p_pos["y"]}
                    
            attacking_dir = self.determine_attacking_direction(shooter["team"], tracked_items)
            
            self.active_shot = {
                "shooter": shooter,
                "start_pos": shooter["pitch_position"],
                "start_timestamp": timestamp,
                "contact_conf": ball_contact_event.get("confidence", 0.0),
                "attacking_dir": attacking_dir
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
            is_dict = isinstance(p, dict)
            class_name = p.get("class_name") if is_dict else getattr(p, "class_name", None)
            mapping_status = p.get("mapping_status") if is_dict else getattr(p, "mapping_status", None)
            
            if class_name == "player" and mapping_status == "mapped":
                pos = p.get("pitch_position") if is_dict else getattr(p, "pitch_position", None)
                if pos:
                    px, py = pos["x"], pos["y"]
                    dist = ((bx - px)**2 + (by - py)**2)**0.5
                    if dist < min_dist:
                        min_dist = dist
                        nearest = p
                    
        if min_dist < 3.0:
            return nearest
        return None
