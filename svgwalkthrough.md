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


---

## Pass Detection & Real-Video Validation (Phase 7B)

**Pass Detection Architecture:**
- Implemented `PassDetectionService` that operates purely on pre-computed signals (bounding boxes, ball contact, pitch positions).
- Tracks a "potential pass" lifecycle: Initial `BallContact` → Ball Disappearance/Transit tracking → Receiver `BallContact` / proximity validation.
- Validates the receiver is on the same team (otherwise it's an interception or turnover).
- Validates temporal proximity (passes taking > 5 seconds are discarded).
- Deduplicates pass frames into a single `PASS_CANDIDATE` event emitted to SQLite and WebSocket.

**Pass Definition (Conservative):**
- A pass candidate is defined as: *A ball-contact event by Player A, followed by ball movement toward Player B (same team), culminating in Player B establishing proximity/contact within a specific temporal window.*
- This is an **AI-generated pass candidate** and does not constitute official statistics unless validated by a VAR official.

**Confidence Formula:**
- Pass confidence is derived structurally: `Base Confidence (0.5) + (Passer Contact Confidence * 0.2) + (Receiver Contact Confidence * 0.2)`. 
- Deductions apply if teams are ambiguous or coordinates are missing.

**Real-Video Validation Observations:**
- Three passing sequences validated from `videoplayback_H6upuuOl.mp4`.
- **Case 1:** Successful short pass in midfield.
- **Case 2:** Long cross; accurately tracked start/end pitch coordinates.
- **Case 3:** Disrupted pass (interception). Appropriately rejected as a PASS_CANDIDATE.
- **False Positives:** Dribbling fast or scrambled tackles occasionally trigger false positive passes due to bounding boxes overlapping or rapidly shifting nearest-player metrics.

**Limitations:**
- No shot or goal detection logic (shots on target may register as uncertain passes).
- Missing pitch coordinates default to rough pixel-distance calculations or `Distance: UNAVAILABLE`.

## Shot Detection (Phase 7C)

**Architecture:**
- Introduces `ShotDetectionService` in `backend/cv/events/shot_detection.py` to identify AI-generated shot candidates.
- Triggered by ball contact events, it observes the ball's trajectory over a customizable time window (e.g. 3.0 seconds).
- Identifies the shooter using position, distance, and contact confidence.
- Utilizes the `team` and pitch mapping coordinates to establish attacking direction.
- Differentiates shots from passes primarily by evaluating distance and trajectory towards the attacking area (opponent's goal side).
- Events are saved to SQLite and broadcast via WebSockets as `SHOT_CANDIDATE`.

**Shot Definition & Confidence:**
- A shot is conservatively defined as a confirmed ball contact followed by the ball traveling a sufficient distance towards the opponent's goal-side region from an attacking position.
- Shot confidence formula: `0.6 + (contact_conf * 0.3)` with a penalty of `-0.2` if the attacking direction or team is unknown, bringing it down to `status="uncertain"`.
- Duplicate shot candidates detected across consecutive frames are aggregated into a single logical event using a temporal deduplication window.

**Validation Results & Limitations:**
- Passes vs Shots are processed independently; if evidence for both exists and they happen concurrently, they are emitted separately as candidates. Often, passes trigger at the receiving end, while shots trigger during the ball's transit.
- No synthetic data is generated. Ambiguous contacts or unobservable goal directions result in `uncertain` statuses or no shot emitted.
- Testing verified the expected progression and geometric logic on mock datasets.
- *False Positives Note*: On the standard test footage (`test_video.mp4`), due to a lack of shots on goal and sparse tracking, no valid shot candidates were generated. This aligns with the strict confidence and distance requirements designed to prevent fabricating false statistical events.

## Goal Detection & Geometry (Phase 7D)

**Architecture:**
- Introduces `GoalGeometry` in `backend/cv/field/goal_geometry.py` to represent real-world pitch boundaries. 
- Introduces `GoalDetectionService` in `backend/cv/events/goal_detection.py` to evaluate ball crossings.
- Integrated into `detection_runner.py` alongside shot and pass detection.

**Goal Geometry Methodology:**
- Uses a standard 105m x 68m pitch coordinate mapping.
- Goal lines are placed precisely at `x = 0.0` (negative X direction) and `x = 105.0` (positive X direction).
- The goal mouth region is defined around the center `y = 34.0`, bounded by the standard 7.32m goal width with a `1.0m` tolerance margin to account for tracking noise.

**Goal Candidate Logic:**
- The system checks if the ball transitions across a defined goal line (`x` changes appropriately) between tracked frames, while the `y` coordinate falls within the goal-mouth boundaries.
- Continuous ball tracking is required; if the ball is lost for an extended time (>2 seconds) before crossing, interpolation is disabled to prevent hallucinated goals (returns insufficient evidence).

**Confidence Score & Validation:**
- A base confidence of 0.85 is granted to clear, continuous crossings. Time gaps between frames due to intermittent tracking apply a penalty.
- **Benchmark Notes:** Evaluated on the baseline test footage (`test_video.mp4`), which only features midfield play. 0 goals were hallucinated/falsely flagged. Due to the lack of real goal footage in the available dataset, accuracy is documented but not falsely validated. 
- **Tests & Deduplication:** Unit tests validated behavior for valid goal mouth crossings, wide shots, and invalid directions. A deduplication window prevents multiple goal events for the same instance.

## Possession & Turnover Intelligence (Phase 7E)

**Architecture:**
- Introduces `PossessionService` in `backend/cv/events/possession.py`.
- Integrates into `detection_runner.py` alongside shot, pass, and goal detection.

**Possession Logic:**
- Tracks the closest player to the ball within a strict spatial threshold (2.5m).
- Requires temporal continuity (e.g., minimum 5 frames) to assert possession.
- Generates `POSSESSION_CHANGE` when control establishes to a teammate, and `TURNOVER_CANDIDATE` when control switches between teams.
- Safely handles ambiguous moments or tracking loss by maintaining the last known possessor without hallucinating rapid turnovers.

**Validation:**
- Integrated completely into the existing EventDatabase and WebSocket pipeline.
- Added `POSSESSION_CHANGE` and `TURNOVER_CANDIDATE` to the React dashboard `EventCard` dictionary.
- Tested via unit tests ensuring temporal stability is respected over simple proximity flashes.
- Benchmark run on real video evaluated fast sequences, successfully suppressing false turnovers when tracking was intermittent.

## Phase 7E.1: Tiki-Taka / One-Touch Possession Handling

**Architecture:**
- Enhanced `PossessionService` to operate a dual-level state machine: `FIRM POSSESSION` and `SHORT TOUCH / ONE-TOUCH POSSESSION`.
- Integrated with `BallContactService` to provide hard evidence of player-ball interaction.
- Allowed state transitions without requiring the ball to remain within 2.5m of the player continuously, resolving rapid sequences like `TOUCH -> PASS -> TOUCH`.

**Configuration Thresholds:**
- `firm_possession_frames`: 5
- `short_touch_min_frames`: 1
- `short_touch_max_frames`: 4
- `distance_threshold_m`: 2.5
- `max_ball_travel_gap_frames`: 60

**Validation:**
- Passed `test_possession.py` containing permutations of 1-frame touches, same-team Tiki-Taka, and opponent interceptions.
- Evaluated on real video with fast passing sequences. Detected one-touch passes and interceptions correctly while suppressing false positives from proximity tracking errors.
