from backend.cv.base import BaseEventDetectionService, CVResult


class EventDetectionService(BaseEventDetectionService):
    @property
    def module_name(self) -> str:
        return "EventDetectionService"

    def is_ready(self) -> bool:
        return False

    def detect_events(self, video_id: str) -> CVResult:
        return CVResult(
            status="not_implemented",
            module_name=self.module_name,
            message="Automated match event detection (goals, fouls, cards, substitutions) is not implemented yet. Pipeline will be configured in the Computer Vision phase.",
            data={"video_id": video_id, "pending_models": ["Action recognition 3D-CNN / Video Transformer"]},
        )
