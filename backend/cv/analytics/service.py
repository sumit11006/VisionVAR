from typing import Any
from backend.cv.base import BasePlayerAnalyticsService, CVResult


class PlayerAnalyticsService(BasePlayerAnalyticsService):
    @property
    def module_name(self) -> str:
        return "PlayerAnalyticsService"

    def is_ready(self) -> bool:
        return False

    def compute_player_metrics(self, player_id: str, tracking_data: Any) -> CVResult:
        return CVResult(
            status="not_implemented",
            module_name=self.module_name,
            message="Dynamic player spatial telemetry, sprint detection, and physical load analysis is not implemented yet. Pipeline will be configured in the Computer Vision phase.",
            data={"player_id": player_id, "pending_analytics": ["Instantaneous speed & acceleration", "Cumulative distance & sprint count", "Pitch heatmap"]},
        )
