# VisionVAR — AI-Powered Football Video Intelligence Platform

VisionVAR is an advanced football video analytics and automated VAR system platform. It features sub-millimeter pitch spatial reconstruction, multi-angle broadcast video synchronization, limb keypoint tracking, and tactical shape intelligence.

```
NEXT.JS FRONTEND
        ↓
REST API / WebSocket
        ↓
FASTAPI BACKEND
        ↓
DATABASE (SQLite / PostgreSQL)
        ↓
CV PIPELINE (Interfaces Mounted)
```

---

## Architecture Overview

### Frontend
- **Framework**: Next.js 14 (App Router) + React 19 + TypeScript
- **Styling**: Tailwind CSS v4 with custom dark sports-analysis design tokens
- **Features**: Live Workspace HUD, Formation & Radar tactical view, Semi-Automated Offside Technology (SAOT) limb review, Player Analytics cockpit, Event Timeline, and Match Summary

### Backend
- **Framework**: FastAPI (Python 3.10+)
- **ORM & Database**: SQLAlchemy 2.0 with SQLite (`data/visionvar.db`) and plug-and-play PostgreSQL compatibility
- **Streaming**: WebSockets for low-latency live telemetry (`/ws/analysis/{session_id}`)
- **Docs**: Auto-generated interactive OpenAPI / Swagger UI at `/docs`
- **CV Architecture**: Modular CV pipelines with YOLOv8 for detection and ByteTrack (`supervision`) for persistent multi-object tracking. Includes abstract service interfaces ready for homography and skeletal models.

---

## Project Structure

```
VisionVAR/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI entry point & CORS
│   │   ├── api/                     # REST API routers & endpoints
│   │   ├── core/                    # App config & DB engine
│   │   ├── models/                  # SQLAlchemy ORM models
│   │   ├── schemas/                 # Pydantic v2 validation models
│   │   ├── services/                # Business logic services
│   │   └── websocket/               # WebSocket connection manager & stream
│   ├── cv/                          # Modular CV service interfaces & placeholders
│   │   ├── detection/               # DetectionService
│   │   ├── tracking/                # TrackingService
│   │   ├── ball/                    # BallTrackingService
│   │   ├── field/                   # PitchMappingService
│   │   ├── offside/                 # OffsideService (SAOT)
│   │   ├── formation/               # FormationService
│   │   ├── events/                  # EventDetectionService
│   │   └── analytics/               # PlayerAnalyticsService
│   ├── data/                        # SQLite DB, uploads & initial seeder
│   ├── tests/                       # Pytest automated test suite
│   └── requirements.txt
│
├── visionvar-app/                   # Next.js frontend application
│   ├── app/                         # App Router pages
│   ├── components/                  # Reusable UI & HUD components
│   ├── lib/api.ts                   # Type-safe API client & WebSocket handler
│   └── types/                       # Shared TypeScript interfaces
│
├── API_CONTRACT.md                  # Comprehensive API specification
└── README.md
```

---

## Getting Started

### 1. Backend Setup

From the repository root or `backend/` directory:

```bash
# 1. Navigate to backend
cd backend

# 2. (Optional) Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Start the FastAPI development server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- **Interactive API Documentation (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative Documentation (ReDoc)**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check**: [http://localhost:8000/api/health](http://localhost:8000/api/health)

### 2. Real Computer-Vision (YOLO) Setup & Execution

#### Ultralytics, PyTorch & Supervision Dependencies
Ultralytics YOLO, OpenCV, and Supervision (for ByteTrack) are included in `backend/requirements.txt`:
```bash
pip install ultralytics opencv-python-headless torch torchvision supervision
```

#### YOLO Model Management
- **Default Model**: `yolov8n.pt` (automatically cached in `models/yolov8n.pt` on first inference).
- **Custom Model Path**: Set the `MODEL_PATH` environment variable:
  ```bash
  # Windows PowerShell
  $env:MODEL_PATH="models/yolov8s.pt"
  # Linux/macOS
  export MODEL_PATH="models/yolov8s.pt"
  ```
- **Where to place models**: Place `.pt` weight files inside the `models/` directory at the repository root.

#### CPU vs CUDA Execution
- **CPU Mode (Default)**: Set `INFERENCE_DEVICE=cpu`. Optimized for universal compatibility without GPU requirements.
- **CUDA / GPU Acceleration**: If an NVIDIA GPU is available with CUDA drivers:
  ```bash
  # Windows PowerShell
  $env:INFERENCE_DEVICE="cuda"
  # Linux/macOS
  export INFERENCE_DEVICE="cuda"
  ```
  VisionVAR will automatically verify `torch.cuda.is_available()` and gracefully fall back to CPU if unavailable.

#### Uploading a Football Video & Starting Detection
1. **Upload Video**:
   ```bash
   curl -X POST "http://localhost:8000/api/videos/upload" \
     -F "file=@path/to/football_match.mp4"
   ```
2. **Start Asynchronous YOLO Detection**:
   ```bash
   curl -X POST "http://localhost:8000/api/analysis/sessions/UCL-2024-MCI-RMA-F/detect" \
     -H "Content-Type: application/json" \
     -d '{"frame_skip": 4, "confidence_threshold": 0.25}'
   ```
3. **Live Stream over WebSocket**:
   Connect your client to `ws://localhost:8000/ws/analysis/UCL-2024-MCI-RMA-F` to stream live `frame_detection` boxes and `processing_status`.
4. **Live Workspace UI**:
   Navigate to [http://localhost:3000/sessions/UCL-2024-MCI-RMA-F](http://localhost:3000/sessions/UCL-2024-MCI-RMA-F) and click **Run YOLO Detect** to see real bounding boxes and confidences overlay live on the video canvas.

### 3. Frontend Setup

In a separate terminal window:

```bash
# 1. Navigate to frontend directory
cd visionvar-app

# 2. Install Node dependencies
npm install

# 3. Run development server
npm run dev
```

- **Application URL**: [http://localhost:3000](http://localhost:3000)

---

## API Endpoints Summary

For complete JSON request and response payloads, see [API_CONTRACT.md](API_CONTRACT.md).

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Service health, DB connectivity, CV status |
| `POST` | `/api/videos/upload` | Multipart video file upload |
| `POST` | `/api/analysis/sessions` | Create new match analysis session |
| `GET` | `/api/analysis/sessions` | List all analysis sessions |
| `GET` | `/api/analysis/sessions/{session_id}` | Get session details & metrics |
| `GET` | `/api/analysis/sessions/{session_id}/status` | Get pipeline execution progress |
| `GET` | `/api/matches/{match_id}` | Match context, score, clock & feeds |
| `GET` | `/api/matches/{match_id}/events` | Match timeline events log |
| `GET` | `/api/matches/{match_id}/players/{player_id}/telemetry` | Player 3D tracking & physical metrics |
| `GET` | `/api/matches/{match_id}/formation` | Tactical formation (CV placeholder) |
| `GET` | `/api/matches/{match_id}/offside` | SAOT offside review (CV placeholder) |
| `WS` | `/ws/analysis/{session_id}` | Live WebSocket telemetry stream |

---

## Running Automated Tests

Run the full pytest suite:

```bash
pytest backend/tests -v
```
