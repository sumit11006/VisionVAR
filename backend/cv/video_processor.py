import os
from pathlib import Path
from typing import Generator, Tuple, Optional
import cv2
import numpy as np


class VideoProcessingError(Exception):
    """Custom exception raised during video loading, extraction, or frame decoding."""
    pass


class VideoProcessor:
    """
    VideoProcessor manages video file lifecycle, metadata extraction,
    and frame decoding using OpenCV.
    """

    SUPPORTED_EXTENSIONS = {".mp4", ".mkv", ".mov", ".avi", ".ts"}

    def __init__(self, video_path: str):
        self.video_path = Path(video_path)
        self.cap: Optional[cv2.VideoCapture] = None

        self.fps: float = 0.0
        self.total_frames: int = 0
        self.width: int = 0
        self.height: int = 0
        self.duration_seconds: float = 0.0

        self._validate_and_open()

    def _validate_and_open(self):
        if not self.video_path.exists():
            raise VideoProcessingError(f"Video file not found at path: {self.video_path}")

        if self.video_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise VideoProcessingError(
                f"Unsupported video format: '{self.video_path.suffix}'. "
                f"Supported formats: {sorted(list(self.SUPPORTED_EXTENSIONS))}"
            )

        if self.video_path.stat().st_size == 0:
            raise VideoProcessingError(f"Video file is empty (0 bytes): {self.video_path}")

        self.cap = cv2.VideoCapture(str(self.video_path))
        if not self.cap.isOpened():
            raise VideoProcessingError(f"Failed to open video file: {self.video_path}")

        # Extract stream properties
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 25.0
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)

        if self.fps > 0 and self.total_frames > 0:
            self.duration_seconds = round(self.total_frames / self.fps, 2)
        else:
            self.duration_seconds = 0.0

        if self.width <= 0 or self.height <= 0 or self.total_frames <= 0:
            self.release()
            raise VideoProcessingError(
                f"Video has invalid dimensions or zero frames: {self.width}x{self.height}, frames: {self.total_frames}"
            )

    @property
    def metadata(self) -> dict:
        return {
            "filename": self.video_path.name,
            "fps": round(self.fps, 2),
            "total_frames": self.total_frames,
            "resolution": f"{self.width}x{self.height}",
            "width": self.width,
            "height": self.height,
            "duration_seconds": self.duration_seconds,
            "size_bytes": self.video_path.stat().st_size,
        }

    def iter_frames(
        self,
        frame_skip: int = 1,
        max_frames: Optional[int] = None,
    ) -> Generator[Tuple[int, float, np.ndarray], None, None]:
        """
        Yields (frame_number, timestamp_seconds, frame_bgr) sequentially.
        If frame_skip > 1, skips frames to improve throughput.
        """
        if not self.cap or not self.cap.isOpened():
            raise VideoProcessingError("Video capture is not open")

        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        frame_idx = 0
        yielded_count = 0

        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret or frame is None:
                break

            if frame_idx % frame_skip == 0:
                timestamp = round(frame_idx / self.fps, 3) if self.fps > 0 else 0.0
                yield frame_idx, timestamp, frame
                yielded_count += 1
                if max_frames and yielded_count >= max_frames:
                    break

            frame_idx += 1

    def release(self):
        if self.cap is not None:
            if self.cap.isOpened():
                self.cap.release()
            self.cap = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

    def __del__(self):
        self.release()
