import pytest
import numpy as np
from backend.cv.team.service import TeamClassificationService
from backend.app.schemas.detection import BoundingBox, TrackedItem

@pytest.fixture
def team_service():
    return TeamClassificationService()

def test_insufficient_frames(team_service):
    # Until 5 tracks are collected, team should be unknown
    import cv2
    frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
    bbox = BoundingBox(x1=0, y1=0, x2=50, y2=100)
    team, conf = team_service.predict_team(1, frame, bbox)
    assert team == "unknown"

def test_referee_is_unknown(team_service):
    # Referee (white) should always be unknown
    frame = np.full((1080, 1920, 3), 255, dtype=np.uint8)
    bbox = BoundingBox(x1=0, y1=0, x2=50, y2=100)
    team, conf = team_service.predict_team(2, frame, bbox)
    assert team == "unknown"

def test_grass_is_unknown(team_service):
    # Grass (green) should be ignored
    import cv2
    hsv = np.full((100, 50, 3), (60, 200, 200), dtype=np.uint8)
    frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    bbox = BoundingBox(x1=0, y1=0, x2=50, y2=100)
    team, conf = team_service.predict_team(3, frame, bbox)
    assert team == "unknown"
