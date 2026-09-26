from typing import Optional
from backend.cv.base import BaseFormationService, CVResult


class FormationService(BaseFormationService):
    @property
    def module_name(self) -> str:
        return "FormationService"

    def is_ready(self) -> bool:
        return False

    def detect_formation(self, match_id: str, frame_window: Optional[int] = None) -> CVResult:
        return CVResult(
            status="not_implemented",
            module_name=self.module_name,
            message="Tactical shape and team formation classification is not implemented yet. Pipeline will be configured in the Computer Vision phase.",
            data={
                "match_id": match_id,
                "frame_window": frame_window,
                "pending_components": [
                    "Temporal mean player centroid clustering",
                    "Hungarian matching against canonical shapes (4-3-3, 4-2-3-1, etc.)",
                    "Compactness and tactical width/depth geometry",
                ],
            },
        )
