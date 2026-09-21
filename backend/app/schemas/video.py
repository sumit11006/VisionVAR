from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class VideoUploadResponse(BaseModel):
    video_id: str
    filename: str
    file_size_bytes: int
    content_type: str
    status: str
    created_at: datetime
    duration_seconds: Optional[float] = None
    fps: Optional[float] = None
    total_frames: Optional[int] = None
    resolution: Optional[str] = None
    session_id: Optional[str] = None
    message: str = "Video uploaded successfully and metadata extracted."


class VideoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    file_size_bytes: int
    content_type: str
    duration_seconds: Optional[float] = None
    fps: Optional[float] = None
    total_frames: Optional[int] = None
    resolution: Optional[str] = None
    status: str
    created_at: datetime
