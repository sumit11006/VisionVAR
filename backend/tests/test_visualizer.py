import cv2
import numpy as np
from backend.cv.detection.visualizer import DetectionVisualizer
from backend.app.schemas.detection import FrameDetectionResult, DetectionItem, BoundingBox


def test_visualizer_annotation():
    # 640x480 black image
    frame = np.zeros((480, 640, 3), dtype=np.uint8)

    detection_result = FrameDetectionResult(
        frame=42,
        timestamp=1.4,
        detections=[
            DetectionItem(
                class_name="player",
                confidence=0.92,
                bbox=BoundingBox(x1=100, y1=150, x2=200, y2=350),
            ),
            DetectionItem(
                class_name="ball",
                confidence=0.88,
                bbox=BoundingBox(x1=300, y1=300, x2=320, y2=320),
            ),
        ],
    )

    annotated = DetectionVisualizer.annotate_frame(frame, detection_result, draw_hud=True)

    assert annotated.shape == (480, 640, 3)
    # The annotated image must not be completely black anymore
    assert np.any(annotated > 0)
    # Ensure original frame wasn't modified in place
    assert np.all(frame == 0)
