from typing import Any
from backend.cv.base import BaseBallTrackingService, CVResult


class BallTrackingService(BaseBallTrackingService):
    @property
    def module_name(self) -> str:
        return "BallTrackingService"

    def is_ready(self) -> bool:
        return False

    def track_ball_trajectory(self, frame_sequence: Any) -> CVResult:
        return CVResult(
            status="not_implemented",
            module_name=self.module_name,
            message="High-speed 3D ball trajectory and velocity analysis is not implemented yet. Pipeline will be configured in the Computer Vision phase.",
            data={"pending_method": "TrackNetV2 / Multi-cam 3D triangulation"},
        )
