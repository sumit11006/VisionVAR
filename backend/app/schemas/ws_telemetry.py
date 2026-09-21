from typing import Optional, Dict, Any, List
from pydantic import BaseModel


class WSTelemetryMessage(BaseModel):
    type: str  # "telemetry_update", "status_update", "heartbeat", "error"
    session_id: str
    timestamp: str
    current_frame: int
    total_frames: int
    fps: float
    cluster_load_percent: float
    inference_ms: float
    ai_confidence: float
    ball_velocity_kph: float
    ball_visibility: str
    active_players_tracked: int
    extra: Optional[Dict[str, Any]] = None
