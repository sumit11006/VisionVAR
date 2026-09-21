from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class MatchEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    minute: int
    second: int = 0
    frameId: int = 0
    timecode: str = "00:00:00:00"
    type: str
    team: str
    player: Optional[str] = None
    playerJersey: Optional[int] = None
    playerTeam: Optional[str] = None
    description: Optional[str] = None
    aiVerdict: Optional[str] = None
    xg: Optional[float] = None
    ballVelocityKph: Optional[float] = None
    impactGForce: Optional[float] = None
    saotMarginCm: Optional[float] = None
    aiExplanation: Optional[str] = None
    isActive: Optional[bool] = False


class MatchEventsListResponse(BaseModel):
    match_id: str
    total_events: int
    events: List[MatchEventResponse]
