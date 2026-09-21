from typing import Optional
from pydantic import BaseModel, ConfigDict


class Team(BaseModel):
    code: str
    name: str


class Score(BaseModel):
    home: int
    away: int


class MatchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    homeTeam: Team
    awayTeam: Team
    score: Score
    clock: str
    period: str
    competition: str
    venue: str
    status: str
    feedSpec: str
    latencyMs: int
