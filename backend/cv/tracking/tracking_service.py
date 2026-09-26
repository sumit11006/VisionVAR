import numpy as np
import supervision as sv
from typing import List, Dict, Any

from backend.app.schemas.detection import DetectionItem, TrackedItem, BoundingBox

class TrackingService:
    def __init__(self):
        # Initialize ByteTrack once per analysis session
        self.tracker = sv.ByteTrack()

    def update(self, detections: List[DetectionItem], frame_number: int, timestamp: float) -> List[TrackedItem]:
        if not detections:
            return []

        boxes = []
        confidences = []
        class_ids = []
        
        for det in detections:
            boxes.append([det.bbox.x1, det.bbox.y1, det.bbox.x2, det.bbox.y2])
            confidences.append(det.confidence)
            class_id = 0 if det.class_name == "player" else 1
            class_ids.append(class_id)
            
        if not boxes:
            return []

        sv_detections = sv.Detections(
            xyxy=np.array(boxes, dtype=np.float32),
            confidence=np.array(confidences, dtype=np.float32),
            class_id=np.array(class_ids, dtype=int)
        )

        # ByteTrack update
        tracked_detections = self.tracker.update_with_detections(sv_detections)

        results = []
        for i in range(len(tracked_detections.xyxy)):
            box = tracked_detections.xyxy[i]
            conf = tracked_detections.confidence[i] if tracked_detections.confidence is not None else 0.0
            class_id = tracked_detections.class_id[i]
            track_id = tracked_detections.tracker_id[i]

            c_name = "player" if class_id == 0 else "ball"

            x1, y1, x2, y2 = float(box[0]), float(box[1]), float(box[2]), float(box[3])
            center_x = (x1 + x2) / 2.0
            center_y = (y1 + y2) / 2.0

            results.append(
                TrackedItem(
                    track_id=int(track_id),
                    class_name=c_name,
                    confidence=float(conf),
                    bbox=BoundingBox(x1=round(x1, 2), y1=round(y1, 2), x2=round(x2, 2), y2=round(y2, 2)),
                    center={"x": round(center_x, 2), "y": round(center_y, 2)},
                    frame=frame_number,
                    timestamp=round(timestamp, 3),
                    state="tracked"
                )
            )

        return results
