from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class MatchEvent(Base):
    __tablename__ = "events"

    id = Column(String, primary_key=True, index=True)
    match_id = Column(String, ForeignKey("matches.id"), nullable=False, index=True)
    minute = Column(Integer, nullable=False)
    second = Column(Integer, default=0)
    frame_id = Column(Integer, default=0)
    timecode = Column(String, default="00:00:00:00")
    type = Column(String, nullable=False)
    team = Column(String, default="")
    player = Column(String, nullable=True)
    player_jersey = Column(Integer, nullable=True)
    player_team = Column(String, nullable=True)
    description = Column(String, nullable=True)
    ai_verdict = Column(String, nullable=True)
    xg = Column(Float, nullable=True)
    ball_velocity_kph = Column(Float, nullable=True)
    impact_g_force = Column(Float, nullable=True)
    saot_margin_cm = Column(Float, nullable=True)
    ai_explanation = Column(String, nullable=True)
    is_active = Column(Boolean, default=False)
    
    # Phase 7A additions
    status = Column(String, nullable=True, default="candidate")
    confidence = Column(Float, nullable=True)
    metadata_json = Column(String, nullable=True)  # Store JSON strings

    # Relationship
    match = relationship("Match", back_populates="events")
