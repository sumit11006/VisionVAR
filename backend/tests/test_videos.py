import io


def test_video_upload_success(client):
    fake_video = io.BytesIO(b"fake mp4 video content byte stream")
    response = client.post(
        "/api/videos/upload",
        files={"file": ("match_clip.mp4", fake_video, "video/mp4")},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "match_clip.mp4"
    assert data["file_size_bytes"] > 0
    assert data["status"] == "UPLOADED"
    assert "vid_" in data["video_id"]


def test_video_upload_invalid_extension(client):
    fake_file = io.BytesIO(b"malicious script")
    response = client.post(
        "/api/videos/upload",
        files={"file": ("hack.exe", fake_file, "application/octet-stream")},
    )
    assert response.status_code == 400
    assert "Unsupported video format" in response.json()["detail"]
