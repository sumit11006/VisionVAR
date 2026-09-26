from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel


class CVResult(BaseModel):
    status: str = "not_implemented"
    module_name: str
    message: str
    contract_version: str = "1.0"
    data: Optional[Dict[str, Any]] = None


class BaseCVService(ABC):
    """Base interface for all VisionVAR Computer Vision pipeline modules."""

    @property
    @abstractmethod
    def module_name(self) -> str:
        """Name of the computer vision service."""
        pass

    @abstractmethod
    def is_ready(self) -> bool:
        """Check if weights, hardware or models are loaded."""
        pass


class BaseDetectionService(BaseCVService):
    @abstractmethod
    def detect_players_and_ball(self, frame_data: Any) -> CVResult:
        pass


class BaseTrackingService(BaseCVService):
    @abstractmethod
    def track_objects(self, detections: Any) -> CVResult:
        pass


class BaseBallTrackingService(BaseCVService):
    @abstractmethod
    def track_ball_trajectory(self, frame_sequence: Any) -> CVResult:
        pass


class BasePitchMappingService(BaseCVService):
    @abstractmethod
    def compute_homography(self, frame_data: Any) -> CVResult:
        pass


class BaseOffsideService(BaseCVService):
    @abstractmethod
    def analyze_offside(self, match_id: str, incident_frame: Optional[int] = None) -> CVResult:
        pass


class BaseFormationService(BaseCVService):
    @abstractmethod
    def detect_formation(self, match_id: str, frame_window: Optional[int] = None) -> CVResult:
        pass


class BaseEventDetectionService(BaseCVService):
    @abstractmethod
    def detect_events(self, video_id: str) -> CVResult:
        pass


class BasePlayerAnalyticsService(BaseCVService):
    @abstractmethod
    def compute_player_metrics(self, player_id: str, tracking_data: Any) -> CVResult:
        pass
