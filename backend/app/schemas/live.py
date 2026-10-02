from pydantic import BaseModel
from typing import Optional

class LiveStartRequest(BaseModel):
    source: str  # e.g., "0" for webcam, "rtsp://...", or "test_video.mp4"
    target_fps: Optional[float] = 15.0
    match_id: Optional[str] = None
    
class LiveSessionResponse(BaseModel):
    session_id: str
    status: str
    source: str
    message: Optional[str] = None
