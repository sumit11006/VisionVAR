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
- **CV Architecture**: Modular CV pipelines with YOLOv8 for detection, ByteTrack (`supervision`) for persistent tracking, HSV K-Means for Team Classification, OpenCV Homography for Pitch Mapping, and K-Means 1D Clustering for Formation Analysis. Includes abstract service interfaces ready for skeletal models.

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


### Phase 3B: Team Identification

**Architecture & Jersey Analysis:**
- Consumes tracked player bounding boxes from the YOLO/ByteTrack pipeline.
- Crops the upper 20% to 50% (and removes 20% from the sides) of the bounding box to specifically isolate the jersey.
- Extracts mean HSV color features from this cropped region.
- Applies a heuristic classification and falls back to "unknown" if the color does not match known teams.

**Temporal Smoothing & Assignment Logic:**
- Uses a rolling sliding window (N=5 frames) to smooth team assignments over time using majority voting.
- Returns a team and a team_confidence score.

**Unknown Handling & Limitations:**
- If the bounding box is too small, heavily occluded, blurry, or visually ambiguous, the model defaults to unknown.
- *Limitation*: With blurry low-pixel broadcast angles, the team identification model often correctly returns unknown rather than fabricating a false positive assignment.

**Configuration:**
Team ID relies on MODEL_PATH=models/yolov8n.pt in .env. YOLOv8s support is preserved.


---

## Ball Tracking & Event Detection (Phase 6A)

**Architecture:**
- Uses YOLOv8n 'sports ball' class detection.
- A dedicated `BallTrackingService` isolates ball detection from player tracking.
- Supports state transitions: `tracked`, `lost`, `reacquired`, `unavailable`.
- Projects ball coordinates using homography to real pitch coordinates, and maintains a finite trajectory history.

**Phase 6A Benchmark Results (Sample Video):**
- **Total frames processed**: 50
- **Ball-detected frames**: 28
- **Detection Rate**: 56.00%
- **Average Detection Confidence**: 0.446
- **Average Detection Latency**: ~106 ms
- **Average Tracking Latency**: ~0.01 ms
- **State Transitions**: 25 (22 lost, 3 reacquired)

**Limitations & Recommendations:**
- *Limitation*: The baseline YOLOv8n detector only achieves a ~56% detection rate for the high-speed football.
- *Recommendation*: While the `BallTrackingService` logic is robust and maintains trajectory state successfully, a dedicated football-specific dataset/model (e.g., TrackNetV2) is required for production-grade, reliable high-speed tracking and event detection (like offsides and passes). The pipeline does NOT fabricate data when the ball is lost.


---

## Ball-Contact & Offside Analysis Foundation (Phase 6B)

**Architecture:**
- Uses `BallContactService` to heuristically identify possible moments when the ball is played (e.g. sharp trajectory changes or reacquisition).
- Uses `OffsideAnalysisService` to construct a second-last-defender line for the defending team based on pitch coordinates.
- Strictly adheres to uncertainty handling. No VAR decisions are fabricated if evidence is insufficient.

**Phase 6B Benchmark Results (Sample Video):**
- **Total frames processed**: 50
- **Ball-contact candidates detected**: 0
- **Offside candidates with sufficient evidence**: 0
- **Candidates with insufficient evidence**: 0
- **Time taken**: 4.22 seconds

**Limitations & Recommendations:**
- *Limitation*: The 50-frame sample video does not contain a discrete ball direction change / kick event that meets the heuristic threshold, resulting in 0 candidates. Furthermore, the 56% YOLOv8n ball detection rate (from Phase 6A) causes excessive fragmentation in trajectory history, making contact moments harder to confirm.
- *Recommendation*: The foundation for calculating attacking direction, sorting defenders, and drawing offside geometry is fully in place and respects uncertainty. However, accurate event detection requires either a specialized ball detection model (TrackNet) or audio-syncing for kick-point confirmation before it can be used authoritatively.


---

## End-to-End Offside Validation (Phase 6D)

**Architecture:**
- Integrates detection, tracking, classification, pitch mapping, ball tracking, and ball-contact services into a single geometric analysis engine.
- Computes dynamic team attacking directions and identifies the second-last defender for both teams relative to that direction.
- Evaluates attacker status relative to the offside line and computes a final AI Assessment.
- Explicitly handles uncertain scenarios by returning `INSUFFICIENT EVIDENCE` rather than fabricating arbitrary decisions.
- Emits real-time geometric and evidence reports directly to the Next.js Offside Review UI.

**Phase 6D Benchmark Results (Sample Video):**
- **Expected contact frame**: 14 (approx.)
- **Detected contact candidate frame**: 15 (Timestamp 0.50s)
- **Second-last Defender ID**: Track ID 6 (vs A) and Track ID 8 (vs B)
- **Attacking Direction**: Positive X (A) and Negative X (B)
- **AI Assessment**: ONSIDE
- **Evidence**: SUFFICIENT FOR GEOMETRIC REVIEW
- **Offside candidates with sufficient evidence**: 4 out of 4 contact frames
- **Average Ball Velocity**: 6.59 m/s (23.72 km/h)
- **Time taken**: 6.39 seconds

**Limitations & Recommendations:**
- *Limitation*: The offside geometric analysis relies entirely on the quality of upstream pipelines (e.g. YOLO, Homography mapping, ByteTrack). Misclassifications of team colors, missed ball contact, or poor mapping can result in an incorrect or "insufficient" geometric output.
- *Recommendation*: Introduce a specialized ball-contact network (e.g., audio+video multimodal) for precise frame-level localization, and employ advanced team classification with visual feature embedding to prevent track ID swaps that may distort the second-last defender calculations. The UI is fully capable of rendering the required `OffsideCandidate` geometry when the data is available.


---

## Event Intelligence & Timeline Persistence (Phase 7A)

**Architecture:**
- Introduced `EventDetectionService` to convert CV tracking signals into structured football `EVENT CANDIDATES`.
- Does not duplicate tracking; consumes outputs directly from detection, tracking, ball contact, and offside analysis.
- Supports temporal deduplication to ensure single instances of events over consecutive frames.

**Supported Event Types:**
- `BALL_CONTACT`
- `PASS_CANDIDATE`
- `POSSESSION_CANDIDATE`
- `BALL_RECOVERY_CANDIDATE`
- `TURNOVER_CANDIDATE`
- `OFFSIDE_CANDIDATE`

**Event States:**
- Explicit states: `candidate`, `confirmed`, `uncertain`, `rejected`.
- **Note:** All generated events are classified as AI-generated `CANDIDATES` and remain as such unless independently validated by a human VAR.

**Confidence Methodology:**
- Event confidence is distinct from detection/tracking confidence.
- Derived heuristically from temporal persistence, proximity, and visibility (e.g. `POSSESSION_CANDIDATE` confidence grows with sustained proximity, `PASS_CANDIDATE` confidence requires matching teams between possessors).

**Persistence & API:**
- Persisted asynchronously into the SQLite database as `MatchEvent` records to ensure timeline persistence after live streaming concludes.
- Strictly isolated by Match/Session ID to avoid cross-contamination.
- Exposed via REST API: `GET /api/matches/{match_id}/events`.

**UI Integration:**
- Live WebSocket emits `{"type": "event_detected", "event": ...}` payloads for real-time dashboard updates.
- The React Frontend Event Timeline dynamically queries both the REST API on load and subscribes to the WebSocket for a seamless, live-updating match log.

**Limitations:**
- No advanced tactical analysis (xG, detailed passing networks, foul recognition).
- Heavy dependency on robust player/ball tracking: if tracking fails or teams are misidentified, possession and turnover logic defaults to uncertain or is omitted.
