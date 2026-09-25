from typing import Optional
import cv2
import numpy as np
from backend.app.schemas.detection import FrameDetectionResult, DetectionItem


class DetectionVisualizer:
    """
    Dedicated visualization utility for rendering computer vision detections onto frames.
    Keeps graphical annotation strictly separated from the inference engine.
    """

    # BGR Color definitions aligned with VisionVAR HUD
    COLOR_PLAYER = (121, 228, 0)    # VisionVAR Neon Emerald (#00e479)
    COLOR_BALL = (0, 215, 255)      # VisionVAR High-Contrast Gold/Yellow (#ffd700)
    COLOR_TEXT = (239, 255, 241)     # High-contrast light text (#f1ffef)
    COLOR_BG = (20, 14, 10)         # Dark cockpit background (#0a0e14)

    @classmethod
    def annotate_frame(
        cls,
        frame_bgr: np.ndarray,
        detection_result: FrameDetectionResult,
        draw_hud: bool = True,
    ) -> np.ndarray:
        """
        Draws bounding boxes, confidence tags, and HUD information onto a copy of the input frame.
        """
        annotated = frame_bgr.copy()
        h, w = annotated.shape[:2]

        # Draw detections
        for det in detection_result.detections:
            cls._draw_detection_box(annotated, det)

        # Draw HUD overlays if requested
        if draw_hud:
            cls._draw_hud_overlay(annotated, detection_result, w, h)

        return annotated

    @classmethod
    def _draw_detection_box(cls, frame: np.ndarray, det: DetectionItem):
        x1, y1 = int(round(det.bbox.x1)), int(round(det.bbox.y1))
        x2, y2 = int(round(det.bbox.x2)), int(round(det.bbox.y2))
        conf_pct = int(round(det.confidence * 100))

        is_ball = det.class_name.lower() == "ball"
        box_color = cls.COLOR_BALL if is_ball else cls.COLOR_PLAYER
        thickness = 2 if is_ball else 2

        # Draw bounding rectangle
        cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, thickness)

        # Label tag
        label = f"{det.class_name.upper()} [{conf_pct}%]"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.4
        font_thickness = 1

        (text_w, text_h), baseline = cv2.getTextSize(label, font, font_scale, font_thickness)
        tag_y1 = max(0, y1 - text_h - 6)
        tag_y2 = y1

        # Background pill
        cv2.rectangle(frame, (x1, tag_y1), (x1 + text_w + 8, tag_y2), box_color, -1)
        # Text in dark color for contrast
        cv2.putText(
            frame,
            label,
            (x1 + 4, tag_y2 - 3),
            font,
            font_scale,
            cls.COLOR_BG,
            font_thickness,
            cv2.LINE_AA,
        )

    @classmethod
    def _draw_hud_overlay(
        cls,
        frame: np.ndarray,
        res: FrameDetectionResult,
        width: int,
        height: int,
    ):
        hud_text = f"FRAME #{res.frame} | T: {res.timestamp:.2f}s | DETECTIONS: {len(res.detections)}"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        font_thickness = 1

        # Semi-transparent top HUD banner
        overlay = frame.copy()
        cv2.rectangle(overlay, (12, 12), (380, 42), cls.COLOR_BG, -1)
        cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)

        # HUD text
        cv2.putText(
            frame,
            hud_text,
            (20, 32),
            font,
            font_scale,
            cls.COLOR_TEXT,
            font_thickness,
            cv2.LINE_AA,
        )
