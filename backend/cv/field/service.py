from typing import Any
from backend.cv.base import BasePitchMappingService, CVResult


class PitchMappingService(BasePitchMappingService):
    @property
    def module_name(self) -> str:
        return "PitchMappingService"

    def is_ready(self) -> bool:
        return False

    def compute_homography(self, frame_data: Any) -> CVResult:
        return CVResult(
            status="not_implemented",
            module_name=self.module_name,
            message="2D-to-3D pitch keypoint homography and camera calibration is not implemented yet. Pipeline will be configured in the Computer Vision phase.",
            data={"pending_method": "Keypoint line detection & DLT homography matrix"},
        )
