import abc
import numpy as np
from typing import List, Optional
from backend.app.schemas.detection import DetectionItem, BoundingBox
from ultralytics import YOLO
import os

class BallDetector(abc.ABC):
    @abc.abstractmethod
    def detect(self, frame_bgr: np.ndarray, conf_threshold: float = 0.12, device: str = "cpu") -> List[DetectionItem]:
        """Detects a ball in the frame and returns a list of DetectionItem."""
        pass

class YOLOBallDetector(BallDetector):
    def __init__(self, model: Optional[YOLO] = None):
        """Optionally share an existing YOLO model to save memory."""
        self._model = model

    def detect(self, frame_bgr: np.ndarray, conf_threshold: float = 0.12, device: str = "cpu") -> List[DetectionItem]:
        if not self._model:
            return []
            
        # Class 32 is 'sports ball' in COCO
        results = self._model(
            frame_bgr,
            conf=conf_threshold,
            device=device,
            classes=[32],
            verbose=False,
        )
        
        detections = []
        if results and len(results) > 0:
            boxes = results[0].boxes
            if boxes is not None:
                for i in range(len(boxes)):
                    cls_id = int(boxes.cls[i].item())
                    if cls_id == 32:
                        conf = float(boxes.conf[i].item())
                        xyxy = boxes.xyxy[i].tolist()
                        
                        detections.append(
                            DetectionItem(
                                class_name="ball",
                                confidence=round(conf, 4),
                                bbox=BoundingBox(
                                    x1=round(xyxy[0], 2),
                                    y1=round(xyxy[1], 2),
                                    x2=round(xyxy[2], 2),
                                    y2=round(xyxy[3], 2),
                                ),
                            )
                        )
        return detections

class FootballSpecificBallDetector(BallDetector):
    def __init__(self, model_path: str = "yolov8m.pt"):
        self.model_path = model_path
        self._model = None
        
    def _load(self):
        if self._model is None:
            self._model = YOLO(self.model_path)
            
    def detect(self, frame_bgr: np.ndarray, conf_threshold: float = 0.12, device: str = "cpu") -> List[DetectionItem]:
        self._load()
        # For yolov8m, class 32 is still sports ball. 
        # If using a fine-tuned model where ball is class 0, this would change.
        # We will assume class 32 or 0 based on model metadata if needed, but for yolov8m it's 32.
        # Let's assume class 32 for standard, or 0 if it's a dedicated 1-class ball model.
        
        # We'll allow classes=[32, 0] and filter by name "ball" or "sports ball".
        results = self._model(
            frame_bgr,
            conf=conf_threshold,
            device=device,
            verbose=False,
        )
        
        detections = []
        if results and len(results) > 0:
            boxes = results[0].boxes
            if boxes is not None:
                for i in range(len(boxes)):
                    cls_id = int(boxes.cls[i].item())
                    class_name = self._model.names.get(cls_id, "")
                    # Accept "sports ball", "ball", "football"
                    if class_name in ("sports ball", "ball", "football"):
                        conf = float(boxes.conf[i].item())
                        xyxy = boxes.xyxy[i].tolist()
                        
                        detections.append(
                            DetectionItem(
                                class_name="ball",
                                confidence=round(conf, 4),
                                bbox=BoundingBox(
                                    x1=round(xyxy[0], 2),
                                    y1=round(xyxy[1], 2),
                                    x2=round(xyxy[2], 2),
                                    y2=round(xyxy[3], 2),
                                ),
                            )
                        )
        return detections

def get_ball_detector(detector_type: str = "yolo", shared_model: Optional[YOLO] = None) -> BallDetector:
    if detector_type == "football_specific":
        return FootballSpecificBallDetector(model_path="yolov8s.pt") # Using yolov8s as alternative for better small object recall
    return YOLOBallDetector(model=shared_model)
