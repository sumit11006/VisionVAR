from typing import Optional
from pydantic import BaseModel, ConfigDict


class Centroid3D(BaseModel):
    x: float
    y: float
    z: float


class PlayerStats(BaseModel):
    distanceKm: float
    sprints: int
    topSpeedKph: float
    avgVelocityKph: float


class PlayerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    jersey: int
    name: str
    team: str
    nationality: str
    role: str
    aiConfidence: float
    skeletalLockStatus: str
    stats: PlayerStats
    centroid: Centroid3D
    pitchX: Optional[float] = None
    pitchY: Optional[float] = None


class PlayerTelemetryResponse(BaseModel):
    player_id: str
    match_id: str
    name: str
    jersey: int
    team: str
    stats: PlayerStats
    centroid: Centroid3D
    pitch_coordinates: dict
    ai_confidence: float
    skeletal_lock_status: str
    instantaneous_speed_kph: float
    acceleration_ms2: float
    stamina_index: float
    timecode: str
