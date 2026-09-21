import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class Video(Base):
    __tablename__ = "videos"

    id = Column(String, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    content_type = Column(String, default="video/mp4")
    duration_seconds = Column(Float, nullable=True)
    fps = Column(Float, nullable=True)
    total_frames = Column(Integer, nullable=True)
    resolution = Column(String, nullable=True)
    status = Column(String, default="UPLOADED")  # UPLOADED, PROCESSING, READY, ERROR
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    sessions = relationship("AnalysisSession", back_populates="video")
