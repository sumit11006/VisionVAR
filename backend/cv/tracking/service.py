from typing import Any
from backend.cv.base import BaseTrackingService, CVResult


class TrackingService(BaseTrackingService):
    @property
    def module_name(self) -> str:
        return "TrackingService"

    def is_ready(self) -> bool:
        return False

    def track_objects(self, detections: Any) -> CVResult:
        return CVResult(
            status="not_implemented",
            module_name=self.module_name,
            message="Multi-object tracking (ByteTrack/BoT-SORT) is not implemented yet. Pipeline will be configured in the Computer Vision phase.",
            data={"pending_framework": "ByteTrack + Kalman Filter", "reid_model": "pending"},
        )
