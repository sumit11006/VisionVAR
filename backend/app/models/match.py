from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class Match(Base):
    __tablename__ = "matches"

    id = Column(String, primary_key=True, index=True)
    home_team_code = Column(String, nullable=False, default="MCI")
    home_team_name = Column(String, nullable=False, default="Manchester City")
    away_team_code = Column(String, nullable=False, default="RMA")
    away_team_name = Column(String, nullable=False, default="Real Madrid")
    score_home = Column(Integer, default=0)
    score_away = Column(Integer, default=0)
    clock = Column(String, default="00:00")
    period = Column(String, default="1ST HALF")
    competition = Column(String, default="UEFA Champions League — Final")
    venue = Column(String, default="Wembley Stadium, London")
    status = Column(String, default="LIVE")  # LIVE, REVIEWING, COMPLETE
    feed_spec = Column(String, default="4K UHD • 60 FPS • 12-CAM OPTICAL ARRAY")
    latency_ms = Column(Integer, default=12)

    # Relationships
    players = relationship("Player", back_populates="match", cascade="all, delete-orphan")
    events = relationship("MatchEvent", back_populates="match", cascade="all, delete-orphan")
    sessions = relationship("AnalysisSession", back_populates="match")
