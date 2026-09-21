from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class BoundingBox(BaseModel):
    x1: float = Field(..., description="Left coordinate in pixels")
    y1: float = Field(..., description="Top coordinate in pixels")
    x2: float = Field(..., description="Right coordinate in pixels")
    y2: float = Field(..., description="Bottom coordinate in pixels")


class DetectionItem(BaseModel):
    class_name: str = Field(..., alias="class", description="'player' or 'ball'")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence score")
    bbox: BoundingBox

    model_config = ConfigDict(populate_by_name=True)


class FrameDetectionResult(BaseModel):
    frame: int = Field(..., ge=0, description="Sequential frame number (0-indexed or 1-indexed)")
    timestamp: float = Field(..., ge=0.0, description="Timestamp in seconds from video start")
    detections: List[DetectionItem] = Field(default_factory=list, description="List of detected objects in the frame")

    model_config = ConfigDict(populate_by_name=True)


class DetectionStartRequest(BaseModel):
    video_id: Optional[str] = Field(None, description="Optional video ID override")
    frame_skip: Optional[int] = Field(None, ge=1, le=30, description="Process every Nth frame")
    confidence_threshold: Optional[float] = Field(None, ge=0.05, le=1.0, description="Minimum confidence cutoff")


class DetectionStartResponse(BaseModel):
    session_id: str
    status: str
    message: str
    total_frames: Optional[int] = None
    fps: Optional[float] = None
    duration_seconds: Optional[float] = None


class WSDetectionFrameMessage(BaseModel):
    type: str = "frame_detection"
    session_id: str
    frame: int
    timestamp: float
    detections: List[DetectionItem]
    inference_time_ms: Optional[float] = None
    total_frames: Optional[int] = None
    fps: Optional[float] = None
    duration_seconds: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None


class WSProcessingStatusMessage(BaseModel):
    type: str = "processing_status"
    session_id: str
    status: str  # "processing", "completed", "error"
    progress: float  # 0.0 to 100.0
    current_frame: Optional[int] = None
    total_frames: Optional[int] = None
    fps: Optional[float] = None
    duration_seconds: Optional[float] = None
    resolution: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    message: Optional[str] = None

class TrackedItem(BaseModel):
    track_id: int = Field(..., description="Unique persistent identifier across frames")
    class_name: str = Field(..., alias="class", description="'player' or 'ball'")
    confidence: float = Field(..., ge=0.0, le=1.0)
    bbox: BoundingBox
    center: dict = Field(..., description="Center coordinates {x, y}")
    frame: int
    timestamp: float
    state: str = Field(..., description="'tracked', 'lost', or 'reacquired'")

    model_config = ConfigDict(populate_by_name=True)

class FrameTrackingResult(BaseModel):
    frame: int
    timestamp: float
    tracked_items: List[TrackedItem]
    
class WSTrackingFrameMessage(BaseModel):
    type: str = "frame_tracking"
    session_id: str
    frame: int
    timestamp: float
    tracked_items: List[TrackedItem]
    inference_time_ms: Optional[float] = None
    tracking_time_ms: Optional[float] = None
    total_frames: Optional[int] = None
    fps: Optional[float] = None
    duration_seconds: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
