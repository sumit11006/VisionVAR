from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class SessionCreateRequest(BaseModel):
    match_id: Optional[str] = Field(None, description="Optional associated match ID")
    video_id: Optional[str] = Field(None, description="Optional uploaded video ID")
    competition: Optional[str] = Field("UEFA Champions League", description="Competition title")
    home_team: Optional[str] = Field("Manchester City", description="Home team name")
    away_team: Optional[str] = Field("Real Madrid", description="Away team name")
    venue: Optional[str] = Field("Wembley Stadium, London", description="Match venue")
    camera_sources: Optional[str] = Field("12-CAM OPTICAL ARRAY", description="Optical capture camera array")


class VideoMetadata(BaseModel):
    video_id: str
    filename: str
    fps: float
    total_frames: int
    duration_seconds: float
    resolution: str
    width: int
    height: int


class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    match_id: Optional[str] = None
    video_id: Optional[str] = None
    homeTeam: str
    awayTeam: str
    competition: str
    venue: str
    status: str
    imageUrl: str
    varAlerts: int = 0
    offsideChecks: int = 0
    penaltyRadar: int = 0
    redCardEval: int = 0
    goalVerify: int = 0
    avgOverturnSeconds: float = 18.4
    processingPercent: Optional[int] = None
    etaMinutes: Optional[int] = None
    cameraSources: Optional[str] = None
    video_metadata: Optional[VideoMetadata] = None
    createdAt: datetime
    updatedAt: datetime


class SessionStatusResponse(BaseModel):
    session_id: str
    status: str
    progress_percent: int
    current_stage: str
    eta_minutes: Optional[int] = None
    detail: str
