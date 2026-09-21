from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class Player(Base):
    __tablename__ = "players"

    id = Column(String, primary_key=True, index=True)
    match_id = Column(String, ForeignKey("matches.id"), nullable=False, index=True)
    jersey = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    team = Column(String, nullable=False)  # e.g. "MCI" or "RMA"
    nationality = Column(String, default="ENG")
    role = Column(String, default="MID")
    ai_confidence = Column(Float, default=98.8)
    skeletal_lock_status = Column(String, default="LOCKED (18/18 KP)")

    # Performance / Physical Stats
    distance_km = Column(Float, default=8.4)
    sprints = Column(Integer, default=24)
    top_speed_kph = Column(Float, default=32.8)
    avg_velocity_kph = Column(Float, default=11.2)

    # 3D Centroid
    centroid_x = Column(Float, default=34.2)
    centroid_y = Column(Float, default=18.6)
    centroid_z = Column(Float, default=1.78)

    # Pitch SVG 2D Projection Coordinates
    pitch_x = Column(Float, default=150.0)
    pitch_y = Column(Float, default=80.0)

    # Relationship
    match = relationship("Match", back_populates="players")
