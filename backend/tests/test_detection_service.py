from unittest.mock import MagicMock, patch
import numpy as np
import pytest

from backend.cv.detection.service import DetectionService, DetectionError
from backend.app.schemas.detection import FrameDetectionResult


def test_detection_service_initialization():
    service = DetectionService(
        model_path="models/yolov8n.pt",
        confidence_threshold=0.35,
        device="cpu",
    )
    assert service.model_path == "models/yolov8n.pt"
    assert service.confidence_threshold == 0.35
    assert service.device == "cpu"
    assert service.module_name == "DetectionService"


def test_detect_frame_with_mock_inference():
    service = DetectionService(confidence_threshold=0.3, device="cpu")

    # Mock Ultralytics YOLO inference output
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)

    mock_box1 = MagicMock()
    mock_box1.cls = [MagicMock(item=lambda: 0)]  # person (player)
    mock_box1.conf = [MagicMock(item=lambda: 0.94)]
    mock_box1.xyxy = [MagicMock(tolist=lambda: [100.0, 150.0, 200.0, 350.0])]

    mock_box2 = MagicMock()
    mock_box2.cls = [MagicMock(item=lambda: 32)]  # sports ball (ball)
    mock_box2.conf = [MagicMock(item=lambda: 0.82)]
    mock_box2.xyxy = [MagicMock(tolist=lambda: [300.0, 300.0, 320.0, 320.0])]

    mock_boxes = MagicMock()
    mock_boxes.__len__.return_value = 2
    mock_boxes.cls = [MagicMock(item=lambda: 0), MagicMock(item=lambda: 32)]
    mock_boxes.conf = [MagicMock(item=lambda: 0.94), MagicMock(item=lambda: 0.82)]
    mock_boxes.xyxy = [
        MagicMock(tolist=lambda: [100.0, 150.0, 200.0, 350.0]),
        MagicMock(tolist=lambda: [300.0, 300.0, 320.0, 320.0]),
    ]

    mock_result = MagicMock()
    mock_result.boxes = mock_boxes

    # Patch the cached model call
    with patch.object(DetectionService, "_model", return_value=[mock_result]):
        result = service.detect_frame(dummy_frame, frame_number=125, timestamp=4.167)

        assert isinstance(result, FrameDetectionResult)
        assert result.frame == 125
        assert result.timestamp == 4.167
        assert len(result.detections) == 2

        # Check player
        player_det = result.detections[0]
        assert player_det.class_name == "player"
        assert player_det.confidence == 0.94
        assert player_det.bbox.x1 == 100.0
        assert player_det.bbox.y2 == 350.0

        # Check ball
        ball_det = result.detections[1]
        assert ball_det.class_name == "ball"
        assert ball_det.confidence == 0.82
        assert ball_det.bbox.x1 == 300.0
