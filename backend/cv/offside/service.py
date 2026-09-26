from typing import Optional
from backend.cv.base import BaseOffsideService, CVResult


class OffsideService(BaseOffsideService):
    @property
    def module_name(self) -> str:
        return "OffsideService"

    def is_ready(self) -> bool:
        return False

    def analyze_offside(self, match_id: str, incident_frame: Optional[int] = None) -> CVResult:
        return CVResult(
            status="not_implemented",
            module_name=self.module_name,
            message="Semi-Automated Offside Technology (SAOT) 3D keypoint projection is not implemented yet. Pipeline will be configured in the Computer Vision phase.",
            data={
                "match_id": match_id,
                "incident_frame": incident_frame,
                "pending_components": [
                    "Limb keypoint skeletal estimation (HRNet/YOLO-Pose)",
                    "Kick-point contact frame detection",
                    "3D virtual offside line projection",
                ],
            },
        )
