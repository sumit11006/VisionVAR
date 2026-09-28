import math
from collections import deque
from typing import List, Dict, Optional, Any
from backend.cv.base import BaseBallTrackingService, CVResult
from backend.app.schemas.detection import DetectionItem

class BallTrackingService(BaseBallTrackingService):
    def __init__(self, history_len=50, max_lost_frames=30):
        self.track_id = 1
        self.state = "unavailable" # "tracked", "lost", "reacquired", "unavailable"
        self.history = deque(maxlen=history_len)
        self.missing_frames = 0
        self.last_position = None  # (cx, cy)
        self.max_lost_frames = max_lost_frames

    @property
    def module_name(self) -> str:
        return "BallTrackingService"

    def is_ready(self) -> bool:
        return True

    def track_ball_trajectory(self, frame_sequence: Any) -> CVResult:
        return CVResult(
            status="ready",
            module_name=self.module_name,
            message="Ball tracking active",
        )

    def _euclidean(self, p1, p2):
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

    def update(self, ball_detections: List[DetectionItem], frame_number: int, timestamp: float) -> Dict[str, Any]:
        best_det = None
        
        if len(ball_detections) == 1:
            best_det = ball_detections[0]
        elif len(ball_detections) > 1:
            if self.last_position is None:
                best_det = max(ball_detections, key=lambda x: x.confidence)
            else:
                best_det = min(
                    ball_detections, 
                    key=lambda d: self._euclidean(
                        ((d.bbox.x1 + d.bbox.x2)/2, (d.bbox.y1 + d.bbox.y2)/2), 
                        self.last_position
                    )
                )

        if best_det is not None:
            cx = (best_det.bbox.x1 + best_det.bbox.x2) / 2.0
            cy = (best_det.bbox.y1 + best_det.bbox.y2) / 2.0
            
            if self.state in ("unavailable", "lost"):
                self.state = "reacquired" if self.state == "lost" else "tracked"
            else:
                self.state = "tracked"
                
            self.missing_frames = 0
            self.last_position = (cx, cy)
            
            return {
                "track_id": self.track_id,
                "state": self.state,
                "image_position": {"x": round(cx, 2), "y": round(cy, 2)},
                "pitch_position": None, 
                "confidence": best_det.confidence,
                "bbox": [best_det.bbox.x1, best_det.bbox.y1, best_det.bbox.x2, best_det.bbox.y2]
            }
        else:
            self.missing_frames += 1
            if self.state in ("tracked", "reacquired"):
                self.state = "lost"
            
            if self.missing_frames > self.max_lost_frames:
                self.state = "unavailable"
                self.last_position = None
                self.history.clear()
                
            return {
                "track_id": self.track_id,
                "state": self.state,
                "image_position": None,
                "pitch_position": None,
                "confidence": 0.0,
                "bbox": None
            }

    def update_pitch_position(self, ball_dict: Dict[str, Any], pitch_coords: tuple):
        if ball_dict and ball_dict.get("state") in ("tracked", "reacquired") and pitch_coords:
            ball_dict["pitch_position"] = {"x": round(pitch_coords[0], 2), "y": round(pitch_coords[1], 2)}
            self.history.append((ball_dict["pitch_position"]["x"], ball_dict["pitch_position"]["y"]))
        return ball_dict
        
    def get_trajectory(self):
        return list(self.history)
