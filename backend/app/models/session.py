import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class AnalysisSession(Base):
    __tablename__ = "analysis_sessions"

    id = Column(String, primary_key=True, index=True)
    match_id = Column(String, ForeignKey("matches.id"), nullable=True, index=True)
    video_id = Column(String, ForeignKey("videos.id"), nullable=True, index=True)
    status = Column(String, default="PROCESSING")  # READY, ARCHIVED, PROCESSING, PENDING, ERROR
    progress_percent = Column(Integer, default=0)
    current_stage = Column(String, default="INITIALIZING")
    eta_minutes = Column(Integer, default=2)

    # Operational metrics
    var_alerts = Column(Integer, default=0)
    offside_checks = Column(Integer, default=0)
    penalty_radar = Column(Integer, default=0)
    red_card_eval = Column(Integer, default=0)
    goal_verify = Column(Integer, default=0)
    avg_overturn_seconds = Column(Float, default=18.4)

    image_url = Column(
        String,
        default="https://images.unsplash.com/photo-1574629810360-7efbbe195018?q=80&w=1200&auto=format&fit=crop",
    )
    camera_sources = Column(String, default="12-CAM OPTICAL ARRAY")

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    match = relationship("Match", back_populates="sessions")
    video = relationship("Video", back_populates="sessions")
