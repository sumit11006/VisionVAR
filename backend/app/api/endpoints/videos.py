from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Depends, status, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from backend.app.schemas.video import VideoUploadResponse, VideoResponse
from backend.app.services.video_service import VideoService
from backend.app.core.database import get_db

router = APIRouter()


@router.post(
    "/upload",
    response_model=VideoUploadResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Videos"],
    summary="Upload match video for CV processing",
)
async def upload_video(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Accepts multipart/form-data video files (MP4, MKV, MOV, AVI, TS).
    Stores file to backend storage, extracts real OpenCV metadata immediately,
    and returns FPS, frame count, resolution, and duration.
    """
    service = VideoService(db)
    video = await service.save_upload(file)

    # Check if a session was created for this video
    session_id = f"session_{video.id}"

    return VideoUploadResponse(
        video_id=video.id,
        filename=video.filename,
        file_size_bytes=video.file_size_bytes,
        content_type=video.content_type,
        status=video.status,
        created_at=video.created_at,
        duration_seconds=video.duration_seconds,
        fps=video.fps,
        total_frames=video.total_frames,
        resolution=video.resolution,
        session_id=session_id,
        message="Video uploaded successfully and OpenCV metadata extracted.",
    )


@router.get(
    "/{video_id}",
    response_model=VideoResponse,
    tags=["Videos"],
    summary="Get video details and metadata",
)
def get_video(video_id: str, db: Session = Depends(get_db)):
    """Retrieve video metadata including OpenCV FPS, frame count, and duration."""
    service = VideoService(db)
    video = service.get_video(video_id)
    return video


@router.get(
    "/{video_id}/file",
    tags=["Videos"],
    summary="Stream video file",
)
def stream_video(video_id: str, db: Session = Depends(get_db)):
    """Stream raw video content for HTML5 video playback."""
    service = VideoService(db)
    video = service.get_video(video_id)
    path = Path(video.file_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Video file not found on disk.")
    return FileResponse(path, media_type=video.content_type)

