# VisionVAR API Contract & Technical Specification

This document details the REST API and WebSocket interfaces provided by the VisionVAR FastAPI backend for consumption by the Next.js frontend and external integrations.

- **Base URL**: `http://localhost:8000/api`
- **WebSocket URL**: `ws://localhost:8000/ws/analysis/{session_id}`
- **Interactive Swagger Docs**: `http://localhost:8000/docs`
- **OpenAPI Schema**: `http://localhost:8000/api/openapi.json`

---

## 1. System Health

### `GET /api/health`
Checks backend service availability, database connectivity, and CV pipeline status.

- **Method**: `GET`
- **Request**: None
- **Response (200 OK)**:
```json
{
  "status": "ok",
  "version": "1.0.0",
  "service": "VisionVAR Backend",
  "database": "connected",
  "cv_pipeline": "standby (interfaces mounted)"
}
```

---

## 2. Video Ingestion

### `POST /api/videos/upload`
Uploads raw match footage for optical analysis and spatial calibration.

- **Method**: `POST`
- **Headers**: `Content-Type: multipart/form-data`
- **Form Data**:
  - `file`: Binary file stream (`.mp4`, `.mkv`, `.mov`, `.avi`, `.ts`)
- **Response (201 Created)**:
```json
{
  "video_id": "vid_2faab3625d70",
  "filename": "ucl_final_first_half.mp4",
  "file_size_bytes": 104857600,
  "content_type": "video/mp4",
  "status": "UPLOADED",
  "created_at": "2026-09-24T03:00:18.123456Z",
  "message": "Video uploaded successfully and stored in backend storage."
}
```
- **Error Response (400 Bad Request)**:
```json
{
  "detail": "Unsupported video format: '.exe'. Supported formats: ['.mp4', '.mkv', '.mov', '.avi', '.ts']"
}
```

---

## 3. Analysis Sessions

### `POST /api/analysis/sessions`
Initializes a new analysis session linked to an uploaded video or match identifier.

- **Method**: `POST`
- **Headers**: `Content-Type: application/json`
- **Request Body**:
```json
{
  "match_id": "UCL-2024-MCI-RMA-F",
  "video_id": "vid_2faab3625d70",
  "competition": "UEFA Champions League",
  "home_team": "Manchester City",
  "away_team": "Real Madrid",
  "venue": "Etihad Stadium",
  "camera_sources": "12-CAM OPTICAL ARRAY"
}
```
- **Response (201 Created)**:
```json
{
  "id": "session_ef2df31880",
  "match_id": "UCL-2024-MCI-RMA-F",
  "video_id": "vid_2faab3625d70",
  "homeTeam": "Manchester City",
  "awayTeam": "Real Madrid",
  "competition": "UEFA Champions League",
  "venue": "Etihad Stadium",
  "status": "PROCESSING",
  "imageUrl": "https://images.unsplash.com/photo-1574629810360-7efbbe195018?q=80&w=1200&auto=format&fit=crop",
  "varAlerts": 0,
  "offsideChecks": 0,
  "penaltyRadar": 0,
  "redCardEval": 0,
  "goalVerify": 0,
  "avgOverturnSeconds": 18.4,
  "processingPercent": 5,
  "etaMinutes": 2,
  "cameraSources": "12-CAM OPTICAL ARRAY",
  "createdAt": "2026-09-24T03:00:18.456789Z",
  "updatedAt": "2026-09-24T03:00:18.456789Z"
}
```

### `GET /api/analysis/sessions`
Returns a list of all historical and active match analysis sessions.

- **Method**: `GET`
- **Response (200 OK)**:
```json
[
  {
    "id": "UCL-2024-MCI-RMA-F",
    "match_id": "UCL-2024-MCI-RMA-F",
    "video_id": null,
    "homeTeam": "Manchester City",
    "awayTeam": "Real Madrid",
    "competition": "UEFA Champions League",
    "venue": "Etihad Stadium",
    "status": "READY",
    "imageUrl": "https://lh3.googleusercontent.com/...",
    "varAlerts": 14,
    "offsideChecks": 9,
    "penaltyRadar": 3,
    "redCardEval": 2,
    "goalVerify": 2,
    "avgOverturnSeconds": 18.4,
    "processingPercent": null,
    "etaMinutes": null,
    "cameraSources": "4-Camera Synchronized VAR feed",
    "createdAt": "2026-09-24T02:57:31.000000Z",
    "updatedAt": "2026-09-24T02:57:31.000000Z"
  }
]
```

### `GET /api/analysis/sessions/{session_id}`
Retrieves details for a specific analysis session.

- **Method**: `GET`
- **Response (200 OK)**: Same schema as `SessionResponse`.
- **Error Response (404 Not Found)**:
```json
{
  "detail": "Analysis session 'invalid-session' not found."
}
```

### `GET /api/analysis/sessions/{session_id}/status`
Returns real-time pipeline execution status and completion percentage.

- **Method**: `GET`
- **Response (200 OK)**:
```json
{
  "session_id": "UCL-2024-MCI-RMA-F",
  "status": "READY",
  "progress_percent": 100,
  "current_stage": "COMPLETE",
  "eta_minutes": 0,
  "detail": "Pipeline is at stage: COMPLETE (100% complete)."
}
```

### `POST /api/analysis/sessions/{session_id}/detect`
Triggers real Ultralytics YOLO computer vision detection on the video associated with the session. Executes asynchronously in the background and broadcasts real-time detection frames over WebSocket.

- **Method**: `POST`
- **Headers**: `Content-Type: application/json`
- **Request Body** (optional):
```json
{
  "video_id": "vid_ucl_action_01",
  "frame_skip": 4,
  "confidence_threshold": 0.25
}
```
- **Response (202 Accepted)**:
```json
{
  "session_id": "UCL-2024-MCI-RMA-F",
  "status": "processing",
  "message": "YOLO player & ball detection initiated in background. Connect to WebSocket /ws/analysis/{session_id} for live stream.",
  "total_frames": null,
  "fps": null,
  "duration_seconds": null
}
```
- **Error Response (404 Not Found)**:
```json
{
  "detail": "Analysis session 'invalid-session' not found."
}
```

---

## 4. Matches, Events, and Telemetry

### `GET /api/matches/{match_id}`
Fetches match context including scoreboard, period, clock, and camera feed spec.

- **Method**: `GET`
- **Response (200 OK)**:
```json
{
  "id": "UCL-2024-MCI-RMA-F",
  "homeTeam": {
    "code": "MCI",
    "name": "Manchester City"
  },
  "awayTeam": {
    "code": "RMA",
    "name": "Real Madrid"
  },
  "score": {
    "home": 2,
    "away": 1
  },
  "clock": "67:24",
  "period": "2H",
  "competition": "UEFA Champions League",
  "venue": "Etihad Stadium",
  "status": "LIVE",
  "feedSpec": "4K RAW 120FPS",
  "latencyMs": 12
}
```

### `GET /api/matches/{match_id}/events`
Retrieves chronologically ordered match timeline events (goals, cards, offsides, VAR interventions).

- **Method**: `GET`
- **Response (200 OK)**:
```json
{
  "match_id": "UCL-2024-MCI-RMA-F",
  "total_events": 10,
  "events": [
    {
      "id": "EVT-001",
      "minute": 12,
      "second": 0,
      "frameId": 21600,
      "timecode": "00:12:00.000",
      "type": "GOAL",
      "team": "MCI",
      "player": "Erling Haaland",
      "playerJersey": 9,
      "playerTeam": "Manchester City / NOR",
      "description": "Clinical finish from Haaland after a through-ball from De Bruyne; right foot placement into far post.",
      "aiVerdict": "VALIDATED",
      "xg": 0.72,
      "ballVelocityKph": 112.4,
      "impactGForce": 18.6,
      "saotMarginCm": null,
      "aiExplanation": "Kick-point confirmed at Frame #21,600. Multi-camera reconstruction validates onside position. Ball in play: verified.",
      "isActive": false
    }
  ]
}
```

### `GET /api/matches/{match_id}/players/{player_id}/telemetry`
Retrieves physical performance metrics and spatial 3D keypoint telemetry for an individual player.

- **Method**: `GET`
- **Response (200 OK)**:
```json
{
  "player_id": "849-19",
  "match_id": "UCL-2024-MCI-RMA-F",
  "name": "Mason Mount",
  "jersey": 19,
  "team": "Chelsea FC / Man City",
  "stats": {
    "distanceKm": 8.42,
    "sprints": 19,
    "topSpeedKph": 32.8,
    "avgVelocityKph": 28.4
  },
  "centroid": {
    "x": 34.08,
    "y": -8.12,
    "z": 1.42
  },
  "pitch_coordinates": {
    "pitch_x": 210.0,
    "pitch_y": 82.0
  },
  "ai_confidence": 98.8,
  "skeletal_lock_status": "OK",
  "instantaneous_speed_kph": 30.7,
  "acceleration_ms2": 2.4,
  "stamina_index": 88.5,
  "timecode": "01:07:24.482"
}
```

---

## 5. Computer Vision Endpoints (Pending Pipeline)

> [!NOTE]
> In accordance with the project instructions, computer vision detection, tracking, offside, and formation algorithms are not faked. These endpoints return explicit `status: "not_implemented"` with standard contracts ready for the CV phase.

### `GET /api/matches/{match_id}/formation`
Tactical shape and centroid clustering endpoint.

- **Method**: `GET`
- **Response (200 OK)**:
```json
{
  "status": "not_implemented",
  "module": "FormationService",
  "match_id": "UCL-2024-MCI-RMA-F",
  "message": "Formation detection pipeline is not implemented yet. Pitch spatial clustering and tactical line analysis will be integrated in the Computer Vision phase.",
  "contract_specification": {
    "expected_payload": {
      "home_formation": "TeamFormation (formation_name, lineup[], compactness_rating, width_meters, depth_meters)",
      "away_formation": "TeamFormation (formation_name, lineup[], compactness_rating, width_meters, depth_meters)",
      "centroid_clustering_confidence": "float (0.0 - 1.0)"
    }
  },
  "data": {
    "match_id": "UCL-2024-MCI-RMA-F",
    "frame_window": null,
    "pending_components": [
      "Temporal mean player centroid clustering",
      "Hungarian matching against canonical shapes (4-3-3, 4-2-3-1, etc.)",
      "Compactness and tactical width/depth geometry"
    ]
  }
}
```

### `GET /api/matches/{match_id}/offside`
Semi-Automated Offside Technology (SAOT) limb keypoint and axis projection endpoint.

- **Method**: `GET`
- **Response (200 OK)**:
```json
{
  "status": "not_implemented",
  "module": "OffsideService",
  "match_id": "UCL-2024-MCI-RMA-F",
  "message": "Semi-Automated Offside Technology (SAOT) limb keypoint & pitch homography pipeline is not implemented yet. Skeleton keypoints, attacker/defender axis projection, and kick-point detection will be integrated in the Computer Vision phase.",
  "contract_specification": {
    "expected_payload": {
      "incident_id": "string",
      "frame_id": "int",
      "timecode": "string",
      "verdict": "'ONSIDE' | 'OFFSIDE'",
      "margin_meters": "float",
      "uncertainty_meters": "float",
      "attacker": "OffsidePlayer (jersey, name, team, body_part_datum, axis_meters, centroid)",
      "defender": "OffsidePlayer (jersey, name, team, body_part_datum, axis_meters, centroid)",
      "ball_contact": "BallContact (timecode, frame_id, ball_speed_kph, confirmed)"
    }
  },
  "data": {
    "match_id": "UCL-2024-MCI-RMA-F",
    "incident_frame": null,
    "pending_components": [
      "Limb keypoint skeletal estimation (HRNet/YOLO-Pose)",
      "Kick-point contact frame detection",
      "3D virtual offside line projection"
    ]
  }
}
```

---

## 6. WebSocket Live Analysis Stream

- **URL**: `ws://localhost:8000/ws/analysis/{session_id}`
- **Protocol**: JSON text frames

### 6.1 Server Handshake (Immediately on connection)
Sent by server upon successful WebSocket connection:
```json
{
  "type": "connected",
  "session_id": "UCL-2024-MCI-RMA-F",
  "timestamp": "2026-09-24T03:00:19.456789Z",
  "message": "Connected to VisionVAR live analysis stream for session 'UCL-2024-MCI-RMA-F'.",
  "telemetry_rate_hz": 10
}
```

### 6.2 Client Request: Ping / Keep-Alive
```json
{
  "action": "ping"
}
```
**Server Response**:
```json
{
  "type": "pong",
  "session_id": "UCL-2024-MCI-RMA-F",
  "timestamp": "2026-09-24T03:00:20.123456Z"
}
```

### 6.3 Client Request: Request Live Telemetry / Scrub Frame
```json
{
  "action": "request_telemetry",
  "frame_id": 121418
}
```
**Server Response**:
```json
{
  "type": "telemetry_update",
  "session_id": "UCL-2024-MCI-RMA-F",
  "timestamp": "2026-09-24T03:00:20.456789Z",
  "current_frame": 121418,
  "total_frames": 162000,
  "fps": 60.0,
  "cluster_load_percent": 74.0,
  "inference_ms": 14.2,
  "ai_confidence": 92.4,
  "ball_velocity_kph": 86.4,
  "ball_visibility": "HIGH",
  "active_players_tracked": 22,
  "optical_calib": "±0.08mm"
}
```

### 6.4 Real YOLO Frame Detection Stream
Broadcast continuously during background video detection for each processed frame:
```json
{
  "type": "frame_detection",
  "session_id": "UCL-2024-MCI-RMA-F",
  "frame": 18,
  "timestamp": 0.6,
  "inference_time_ms": 138.8,
  "detections": [
    {
      "class": "player",
      "confidence": 0.8179,
      "bbox": {
        "x1": 381.0,
        "y1": 232.05,
        "x2": 822.13,
        "y2": 606.5
      }
    },
    {
      "class": "ball",
      "confidence": 0.9644,
      "bbox": {
        "x1": 981.46,
        "y1": 548.79,
        "x2": 1037.54,
        "y2": 607.52
      }
    }
  ]
}
```

### 6.5 Background Detection Processing Status
Broadcast when status changes or progress advances:
```json
{
  "type": "processing_status",
  "session_id": "UCL-2024-MCI-RMA-F",
  "status": "processing",
  "progress": 40.0,
  "current_frame": 24,
  "total_frames": 60
}
```
And upon pipeline completion:
```json
{
  "type": "processing_status",
  "session_id": "UCL-2024-MCI-RMA-F",
  "status": "completed",
  "progress": 100.0,
  "current_frame": 60,
  "total_frames": 60,
  "message": "YOLO detection completed. Processed 10 frames."
}
```
