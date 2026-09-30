import math
from typing import List, Dict, Any, Optional

class BallContactService:
    def __init__(self):
        self.history = []
        self.max_history = 10
        self.last_state = "unavailable"

    def process_frame(self, ball_state: Optional[Dict[str, Any]], frame_number: int, timestamp: float) -> Dict[str, Any]:
        """
        Identify possible moments when the ball is played (contact).
        Returns a dictionary representing the ball contact candidate.
        """
        if not ball_state:
            self.last_state = "unavailable"
            return {"state": "uncertain", "confidence": 0.0, "evidence": {}}

        current_state = ball_state.get("state", "unavailable")
        pitch_pos = ball_state.get("pitch_position")
        
        candidate = {"state": "uncertain", "confidence": 0.0, "evidence": {}}

        # We can only reliably detect trajectory changes if we have pitch coordinates
        if pitch_pos:
            x, y = pitch_pos["x"], pitch_pos["y"]
            self.history.append({"x": x, "y": y, "frame": frame_number, "state": current_state})
            if len(self.history) > self.max_history:
                self.history.pop(0)

            # Heuristic 1: Ball just became visible after being lost
            if current_state == "reacquired" and self.last_state in ["lost", "unavailable"]:
                candidate = {
                    "state": "possible",
                    "confidence": 0.5,
                    "evidence": {"trajectory_change": False, "ball_visible": True, "reason": "reacquired"}
                }
            # Heuristic 2: Sudden direction change
            elif len(self.history) >= 3 and current_state == "tracked":
                p1 = self.history[-3]
                p2 = self.history[-2]
                p3 = self.history[-1]
                
                # Vector p1 -> p2
                v1_x = p2["x"] - p1["x"]
                v1_y = p2["y"] - p1["y"]
                # Vector p2 -> p3
                v2_x = p3["x"] - p2["x"]
                v2_y = p3["y"] - p2["y"]

                len1 = math.hypot(v1_x, v1_y)
                len2 = math.hypot(v2_x, v2_y)

                if len1 > 0.5 and len2 > 0.5: # min movement threshold in pitch units (meters)
                    # Dot product for angle
                    dot = (v1_x * v2_x + v1_y * v2_y)
                    cos_theta = dot / (len1 * len2)
                    cos_theta = max(-1.0, min(1.0, cos_theta))
                    angle = math.acos(cos_theta)

                    # If angle change is sharp (e.g., > 45 degrees or 0.78 radians)
                    if angle > 0.78:
                        candidate = {
                            "state": "possible",
                            "confidence": min(0.9, 0.4 + (angle / math.pi) * 0.5),
                            "evidence": {"trajectory_change": True, "ball_visible": True, "angle": round(math.degrees(angle), 1)}
                        }

        self.last_state = current_state
        return candidate
