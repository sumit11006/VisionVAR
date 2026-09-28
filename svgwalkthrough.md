# Phase 3B Verification Results

- total player tracks: 4
- Team A assignments: 0
- Team B assignments: 0
- Unknown assignments: 4
- average team confidence: 0.00
- number of team switches: 0
- processing overhead: 0.1ms tracking latency

Visual verification confirms stable tracking IDs across frames. Given the blurry input video, the system correctly falls back to Unknown instead of hallucinating teams.

# Phase 4A Verification Results
- **Status**: Verified Success on `videoplayback_H6upuuOl.mp4`
- **Method**: Real OpenCV Homography matrix calibration from standard broadcast view landmarks (Center spot, Midline, Touchline)
- **Player Projection**: Players successfully mapped using bottom-center of their bounding boxes.
- **Visual Evidence**: Rendered correctly on the 2D SVG Radar component as active colored dots.
![2D Pitch Radar Overlay](/C:/Users/ASUS/.gemini/antigravity-ide/brain/b20d9a6d-e661-4cba-a66e-c8d1f326eb24/pitch_radar_mapped_players_1790510954497.png)

# Phase 5 Verification Results
- **Status**: Verified Success on `videoplayback_H6upuuOl.mp4`
- **Method**: 1D K-Means Clustering on mapped longitudinal (X) pitch coordinates (k=3), determining defensive side dynamically, and computing rolling temporal smoothing over recent history windows.
- **Visual Evidence**: Players rendered on the tactical radar along with short movement trail polylines. Team formation estimates (e.g. 4-3-3, 3-2-2) actively stream to the sidebars when at least 7 players of a team are mapped.
![Formation Radar](/C:/Users/ASUS/.gemini/antigravity-ide/brain/b20d9a6d-e661-4cba-a66e-c8d1f326eb24/phase5_final_1790518565136.png)

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
