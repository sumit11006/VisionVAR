import uuid
from typing import List, Dict, Any, Optional
from backend.cv.field.goal_geometry import GoalGeometry

class GoalDetectionService:
    def __init__(self, deduplication_window: float = 5.0):
        self.geometry = GoalGeometry()
        self.deduplication_window = deduplication_window
        
        self.last_ball_pos = None
        self.last_ball_timestamp = None
        
        self.last_emitted_goal = None
        
    def process(
        self,
        frame_idx: int,
        timestamp: float,
        session_id: str,
        match_id: str,
        ball_state: Optional[Dict[str, Any]],
        attacking_directions: Dict[str, str] = None, # team -> direction
        active_shots: List[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        events = []
        
        if not ball_state or ball_state.get("state") not in ["tracked", "reacquired"] or not ball_state.get("pitch_position"):
            if ball_state and ball_state.get("state") == "lost":
                # Do not interpolate. Wait until tracked.
                pass
            return events
            
        curr_pos = ball_state["pitch_position"]
        curr_x, curr_y = curr_pos["x"], curr_pos["y"]
        
        if self.last_ball_pos and self.last_ball_timestamp is not None:
            time_diff = timestamp - self.last_ball_timestamp
            
            # If time gap is too large, tracking was discontinuous. We should still check if it teleported across,
            # but that usually implies tracking error. Let's still evaluate but with lower confidence if gap > 1.0s.
            if time_diff < 2.0:
                prev_x, prev_y = self.last_ball_pos["x"], self.last_ball_pos["y"]
                
                # Check both goal lines
                for team, direction in (attacking_directions or {}).items():
                    if direction in ["positive_x", "negative_x"]:
                        if self.geometry.did_cross_line(prev_x, curr_x, direction):
                            # Interpolate Y at the exact crossing X
                            goal_line_x = self.geometry.get_goal_line(direction)
                            if curr_x != prev_x:
                                t = (goal_line_x - prev_x) / (curr_x - prev_x)
                                crossing_y = prev_y + t * (curr_y - prev_y)
                            else:
                                crossing_y = curr_y
                                
                            if self.geometry.is_in_goal_mouth(crossing_y):
                                # Valid crossing!
                                
                                confidence = 0.85
                                if time_diff > 0.5:
                                    confidence -= 0.2
                                    
                                goal_event = {
                                    "id": str(uuid.uuid4()),
                                    "match_id": match_id,
                                    "session_id": session_id,
                                    "event_type": "GOAL_CANDIDATE",
                                    "timestamp": timestamp,
                                    "frame": frame_idx,
                                    "status": "candidate",
                                    "confidence": max(0.1, confidence),
                                    "team": team,
                                    "metadata": {
                                        "goal_side": direction,
                                        "goal_line_x": goal_line_x,
                                        "crossing_y": round(crossing_y, 2),
                                        "time_gap": round(time_diff, 2)
                                    }
                                }
                                
                                # Deduplication
                                if not self.last_emitted_goal or \
                                   (timestamp - self.last_emitted_goal["timestamp"] > self.deduplication_window) or \
                                   (self.last_emitted_goal["metadata"]["goal_side"] != direction):
                                    events.append(goal_event)
                                    self.last_emitted_goal = goal_event

        self.last_ball_pos = curr_pos
        self.last_ball_timestamp = timestamp
        
        return events
