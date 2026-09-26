import os
import tempfile
from pathlib import Path
import pytest
import cv2
import numpy as np

from backend.cv.video_processor import VideoProcessor, VideoProcessingError


@pytest.fixture
def synthetic_video_path(tmp_path):
    """Generates a small valid MP4 video using OpenCV for testing."""
    video_file = tmp_path / "test_match_clip.mp4"
    width, height = 320, 240
    fps = 30.0
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(str(video_file), fourcc, fps, (width, height))

    # Write 15 synthetic frames with a moving white circle (simulating a ball)
    for i in range(15):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        # Green pitch background
        frame[:] = (34, 139, 34)
        # Moving circle
        cv2.circle(frame, (20 + i * 15, 120), 8, (255, 255, 255), -1)
        out.write(frame)

    out.release()
    return str(video_file)


def test_video_metadata_extraction(synthetic_video_path):
    with VideoProcessor(synthetic_video_path) as vp:
        assert vp.fps == 30.0
        assert vp.total_frames == 15
        assert vp.width == 320
        assert vp.height == 240
        assert vp.duration_seconds == 0.5
        meta = vp.metadata
        assert meta["resolution"] == "320x240"
        assert meta["total_frames"] == 15


def test_video_sequential_frames_reading(synthetic_video_path):
    with VideoProcessor(synthetic_video_path) as vp:
        frames = list(vp.iter_frames(frame_skip=1))
        assert len(frames) == 15
        idx, ts, frame_bgr = frames[0]
        assert idx == 0
        assert ts == 0.0
        assert frame_bgr.shape == (240, 320, 3)

        # Test frame skip
        frames_skipped = list(vp.iter_frames(frame_skip=2))
        assert len(frames_skipped) == 8  # 0, 2, 4, 6, 8, 10, 12, 14


def test_video_file_not_found():
    with pytest.raises(VideoProcessingError) as exc_info:
        VideoProcessor("non_existent_clip_12345.mp4")
    assert "not found" in str(exc_info.value).lower()


def test_video_unsupported_format(tmp_path):
    bad_file = tmp_path / "test.txt"
    bad_file.write_text("not a video")
    with pytest.raises(VideoProcessingError) as exc_info:
        VideoProcessor(str(bad_file))
    assert "unsupported video format" in str(exc_info.value).lower()


def test_video_empty_file(tmp_path):
    empty_file = tmp_path / "empty.mp4"
    empty_file.touch()
    with pytest.raises(VideoProcessingError) as exc_info:
        VideoProcessor(str(empty_file))
    assert "empty" in str(exc_info.value).lower()
