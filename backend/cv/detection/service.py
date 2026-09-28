import os
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
import numpy as np

from backend.app.core.config import settings
from backend.app.schemas.detection import (
    BoundingBox,
    DetectionItem,
    FrameDetectionResult,
)
from backend.cv.base import BaseDetectionService, CVResult


class DetectionError(Exception):
    """Exception raised when YOLO model loading or inference fails."""
    pass


class DetectionService(BaseDetectionService):
    """
    YOLO Computer Vision Detection Service.
    Loads and caches an Ultralytics YOLO model once and runs inference on video frames.
    Extracts bounding boxes and confidence scores for players and the football.
    """

    # Mapping COCO class IDs to VisionVAR domain entities
    TARGET_CLASSES = {
        0: "player",       # COCO 'person'
        32: "ball",        # COCO 'sports ball'
    }

    _instance: Optional["DetectionService"] = None
    _model: Any = None

    def __init__(
        self,
        model_path: Optional[str] = None,
        confidence_threshold: Optional[float] = None,
        device: Optional[str] = None,
    ):
        self.model_path = model_path or settings.MODEL_PATH
        self.confidence_threshold = (
            confidence_threshold if confidence_threshold is not None else settings.CONFIDENCE_THRESHOLD
        )
        self.device = device or settings.INFERENCE_DEVICE
        self._load_model()

    @property
    def module_name(self) -> str:
        return "DetectionService"

    def is_ready(self) -> bool:
        return self._model is not None

    def _load_model(self):
        """Loads the Ultralytics YOLO model once and caches it."""
        if DetectionService._model is not None:
            return

        try:
            from ultralytics import YOLO

            # Resolve model path. If local file doesn't exist yet, Ultralytics auto-downloads YOLOv8n
            path_obj = Path(self.model_path)
            if not path_obj.is_absolute() and not path_obj.exists():
                # Check inside project models/ directory or fallback to model name (e.g. 'yolov8n.pt')
                if (Path("models") / self.model_path).exists():
                    self.model_path = str(Path("models") / self.model_path)
                elif not path_obj.name.endswith(".pt"):
                    self.model_path = f"{path_obj.name}.pt"

            # Create models directory if needed
            Path("models").mkdir(parents=True, exist_ok=True)

            # Initialize YOLO instance
            DetectionService._model = YOLO(self.model_path)

            # Move to target device if supported
            import torch
            if self.device == "cuda" and not torch.cuda.is_available():
                self.device = "cpu"

        except Exception as e:
            raise DetectionError(f"Failed to load YOLO model from '{self.model_path}': {str(e)}") from e

    def detect_frame(
        self,
        frame_bgr: np.ndarray,
        frame_number: int = 0,
        timestamp: float = 0.0,
        conf_threshold: Optional[float] = None,
    ) -> FrameDetectionResult:
        """
        Executes YOLO inference on a single BGR frame.
        Returns validated FrameDetectionResult with player and ball bounding boxes.
        """
        if DetectionService._model is None:
            self._load_model()

        threshold = conf_threshold if conf_threshold is not None else self.confidence_threshold
        detections: List[DetectionItem] = []

        try:
            # 1. Player Detection (using base YOLO model)
            results = DetectionService._model(
                frame_bgr,
                conf=threshold,
                device=self.device,
                classes=[0], # Person only
                verbose=False,
            )

            if results and len(results) > 0:
                boxes = results[0].boxes
                if boxes is not None:
                    for i in range(len(boxes)):
                        cls_id = int(boxes.cls[i].item())
                        conf = float(boxes.conf[i].item())
                        xyxy = boxes.xyxy[i].tolist()  # [x1, y1, x2, y2]
                        
                        if cls_id == 0:
                            detections.append(
                                DetectionItem(
                                    class_name="player",
                                    confidence=round(conf, 4),
                                    bbox=BoundingBox(
                                        x1=round(xyxy[0], 2),
                                        y1=round(xyxy[1], 2),
                                        x2=round(xyxy[2], 2),
                                        y2=round(xyxy[3], 2),
                                    ),
                                )
                            )

            # 2. Ball Detection via Abstraction
            detector_type = os.getenv("BALL_DETECTOR", "yolo")
            from backend.cv.detection.ball import get_ball_detector
            ball_detector = get_ball_detector(detector_type, DetectionService._model)
            
            inference_conf = min(0.12, threshold)
            ball_detections = ball_detector.detect(frame_bgr, conf_threshold=inference_conf, device=self.device)
            detections.extend(ball_detections)

            return FrameDetectionResult(
                frame=frame_number,
                timestamp=round(timestamp, 3),
                detections=detections,
            )

        except Exception as e:
            raise DetectionError(f"Inference failed on frame #{frame_number}: {str(e)}") from e

    def detect_players_and_ball(self, frame_data: Any) -> CVResult:
        """Compatibility wrapper for BaseDetectionService interface."""
        if not self.is_ready():
            return CVResult(
                status="error",
                module_name=self.module_name,
                message="Model not loaded",
            )
        try:
            res = self.detect_frame(frame_data)
            return CVResult(
                status="ready",
                module_name=self.module_name,
                message=f"Detected {len(res.detections)} objects",
                data=res.model_dump(),
            )
        except Exception as e:
            return CVResult(
                status="error",
                module_name=self.module_name,
                message=str(e),
            )
