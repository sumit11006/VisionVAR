# VisionVAR â€” Stitch Export Technical Analysis

> **Source of truth:** `stitch_visionvar_football_intelligence_platform/`  
> **Analysis date:** 2026-09-24  
> **Analyst:** Antigravity IDE (automated deep scan)

---

## 1. Current Architecture

### 1.1 Export Format

The Stitch export produces **flat, self-contained HTML files** â€” one per screen. Each file is a monolithic document bundling:

| Layer | Implementation |
|---|---|
| **Markup** | Semantic HTML5 with extensive `div` nesting for HUD overlays |
| **Styling** | Tailwind CSS v3 via **CDN** (`cdn.tailwindcss.com`) with `forms` and `container-queries` plugins |
| **Design tokens** | Inlined `script#tailwind-config` block, duplicated verbatim in every file |
| **Typography** | Google Fonts CDN â€” Space Grotesk, Inter, JetBrains Mono, Material Symbols |
| **Icons** | Google Material Symbols Outlined (variable web font) |
| **Images** | External `lh3.googleusercontent.com` â€” AI-generated broadcast stills |
| **Interactivity** | Vanilla JS `script` blocks at end of body |
| **Routing** | None â€” all `a href="#"` are non-functional stubs |

### 1.2 What Is NOT Present

- No build tool (no Webpack / Vite / Rollup)
- No component framework (no React / Vue / Svelte)
- No CSS preprocessor (no SCSS / PostCSS pipeline)
- No state management
- No routing layer
- No API calls or data fetching
- No WebSocket connections (though referenced in mock content)
- No authentication layer
- No i18n
- No automated tests

---

## 2. Screen Inventory

| # | Folder | HTML Title | Active Nav Tab | Screenshot |
|---|---|---|---|---|
| 1 | `ultra_high_definition_broadcast_â€¦` | *(no HTML)* | â€” | PNG only |
| 2 | `visionvar_ingestion_neural_pipeline` | VisionVAR â€” Neural Pitch Intelligence System | Live Workspace | yes |
| 3 | `visionvar_pitch_intelligence_var_operations_suite` | VisionVAR â€” Neural Pitch Intelligence System *(duplicate)* | Live Workspace | no |
| 4 | `visionvar_live_analysis_workspace` | VisionVAR â€” Live Workspace | Live Workspace | yes |
| 5 | `visionvar_dedicated_var_offside_review` | VisionVAR - Offside Review Calibrated Engine | Offside Review | yes |
| 6 | `visionvar_tactical_pitch_formation_radar` | VisionVAR - Formation Analysis & Tactical Radar | Formation & Radar | yes |
| 7 | `visionvar_event_timeline_incident_scrubber` | VisionVAR â€” Event Timeline & Incident Scrubber | Event Timeline | yes |
| 8 | `visionvar_player_analytics_biometrics` | VisionVAR â€” Player Analytics & Skeletal Tracking Dossier | Player Analytics | yes |
| 9 | `visionvar_match_summary_var_audit_dossier` | VisionVAR â€” Match Summary & Post-Game VAR Audit Dossier | Match Summary | yes |
| 10 | `visionvar_pitch_intelligence` | DESIGN.md only (no HTML) | â€” | no |

**Canonical 6-route navigation** (observed across all nav bars):

1. **Live Workspace** â€” Primary operator view with live 4K feed + CV overlays
2. **Offside Review** â€” Dedicated SAOT / homography 3D plane calibration
3. **Formation & Radar** â€” 2D tactical pitch radar + formation analysis
4. **Event Timeline** â€” Multi-track incident scrubber + event log
5. **Player Analytics** â€” Individual player biometrics + skeletal tracking dossier
6. **Match Summary** â€” Post-match VAR audit dossier

> **Note:** Folders 2 and 3 contain identical HTML. The ingestion pipeline functions as a **pre-match / dashboard / session-selector** â€” the entry point outside the 6-route nav.

---

## 3. Screen-by-Screen Feature Summary

### Screen 1 â€” ultra_high_definition_broadcast (PNG only)
- Raw broadcast still / splash screen reference. No HTML counterpart.

### Screen 2 â€” Ingestion / Neural Pipeline (Entry / Dashboard)
- **Hero strip**: total frames 162,000 | GPU cluster 74% | inference 14.2ms | optical calib Â±0.08mm
- **Upload actions**: "Upload Match Video" (local/S3) and "Connect Live Optical Pitch Feed" (RTSP/SDI)
- **6-stage pipeline progress cards**: Ingestion â†’ DeepLab â†’ YOLOv9 â†’ Jersey OCR â†’ Homography 3D â†’ VAR Engine
- **Live log terminal strip**: timestamped inference output
- **Recent sessions grid**: 3 match cards (Ready / Archived / Processing)
- **Footer**: UEFA compliance badge, server cockpit ID

### Screen 3 â€” Pitch Intelligence VAR Ops Suite
- Identical HTML to Screen 2. Stitch duplication artefact.

### Screen 4 â€” Live Analysis Workspace
- **Full-bleed video canvas** (16:9, 76vh)
- **CV HUD overlays**: player bounding boxes with corner reticles, ball crosshair, SVG trajectory arc
- **Top-left pill**: camera angle switcher (Main Broadcast / High End-Zone / Tactical 16m / Reverse Angle)
- **Top-right pill**: layer toggles (Bounding Box / Vector Arc / Offside Plane)
- **Bottom-left HUD**: timecode, frame counter, tracking confidence
- **Bottom-right HUD**: Flag Anomaly / Export Event Clip buttons
- **Transport strip**: multi-track scrubber, play/pause/step, speed selector (0.25xâ€“2x), zoom
- **Bottom bento tri-cluster**: Live Pitch Centroid Radar | Live Model Inference Stream | Active Player Telemetry
- **JavaScript**: functional play/pause, scrubber sync, camera switcher, overlay toggles

### Screen 5 â€” VAR Offside Review
- **Review HUD banner**: match score, incident badge "INCIDENT REVIEW: POSSIBLE OFFSIDE", frame ID
- **Calibration viewport** (16:9): freeze-frame with 3D plane overlays
  - Red laser plane â€” Defender Dier #15 @ 34.22m
  - Cyan laser plane â€” Attacker Mount #19 @ 34.08m
  - Delta graphic "Î” +14cm"
  - SVG vanishing perspective grid
- **Floating HUDs**: camera calibration tag | ball contact sub-frame thumbnail | telemetry margin badge | camera switcher
- **Sub-frame stepper**: -5f/-1f/+1f/+5f buttons, sync button
- **Calibration tool toggles**: Kick-Point Anchor Selector, Manual Vanishing Point Toggle
- **Bento 3-grid**: Attacker Locomotion Vector | Second-Last Defender Datum | Official Audit & Export Dispatch
- **Primary CTA**: "Send AI Offside Dossier to Review Official"

### Screen 6 â€” Tactical Pitch Formation Radar
- **Main SVG pitch map**: player centroid dots (cyan = Team A, emerald = Team B), pressure zones, defensive line
- **Formation labels**: 4-3-3 vs 4-2-3-1
- **Sidebar telemetry panels**: possession %, pressing zones, line-breaking pass frequency
- **Interactive player selection** on pitch map
- **Formation control toggles**

### Screen 7 â€” Event Timeline / Incident Scrubber
- **Interactive multi-track timeline** (5 tracks: Goals/xG | Fouls & Cards | Offside Flags | VAR Interventions | Substitutions)
- **Period tabs**: 1st Half / Halftime / 2nd Half / Extra Time
- **Playhead needle** with timestamp badge
- **Event cards (left column)**: timestamp | event type badge | AI verdict badge | player row | 4-col micro-stat bento | AI explanation block
  - Card states: Active (glowing border) / Inactive (hover only)
- **Multi-angle optical inspector (right column)**: freeze-frame + VAR overlays + 3-up camera thumbnails
- **Filter chips**: All (48) / Goals (3) / Shots on Target (11) / VAR Interventions (4) / Offsides (6) / High-Danger Fouls (8) / Tackles (16)

### Screen 8 â€” Player Analytics & Biometrics
- **Player roster grid** (left): jersey number, name, team, AI tracking confidence cards
- **Selected player dossier (right)**: movement heatmap on SVG pitch | sprint profile histogram | skeletal tracking keypoint confidence | biometric stats | offside involvement log
- **Player selector tabs**: switch between players

### Screen 9 â€” Match Summary / VAR Audit Dossier
- **Official identity strip**: referee D. ROSETTI (VAR-1), match metadata
- **Scorecard hero**: MCI 2-1 RMA, competition, venue, final time
- **VAR decision log table**: timestamp | player | type | AI verdict | decision outcome
- **Aggregate telemetry**: total offsides, VAR interventions, goal-line decisions
- **Export controls**: JSON / VAR3D, broadcast-ready graphics flag
- **Official sign-off button**

---

## 4. Reusable Components

The following patterns appear across multiple screens and must become shared React components.

### 4.1 TopNavBar (all 6 screens)
`[Brand Logo + Version badge] | [Nav links with active underline] | [Export + Broadcast Stream + icon buttons] | [Avatar]`

- Sticky h-14, backdrop-blur-xl, bg-surface-container-low/80
- Active link: border-b-2 border-primary-fixed-dim text-primary-fixed-dim
- Icon buttons: videocam, settings, fullscreen
- Primary CTA: "Broadcast Stream" (bg-primary-container)
- Secondary CTA: "Export Telemetry"
- **Inconsistency**: brand icon varies (troubleshoot / videocam / radar); version badge varies â€” needs one canonical definition

### 4.2 MatchStatusBar (Live Workspace, Offside Review)
`[Match score pill: MCI 2-1 RMA | 67:24 2H] | [Incident status badge] | [AI confidence + view toggles]`

### 4.3 BentoTelemetryCard (Live Workspace, Offside Review, Event Timeline)
- bg-surface-container-low card with icon header, 2-col or 4-col micro-stat grid, footer action row

### 4.4 TelemetryChip
- bg-surface-container-lowest | label: 9px JetBrains Mono | value: label-lg bold
- Used in event cards, player telemetry, bento grids

### 4.5 PitchSVGRadar (Live Workspace, Formation Radar, Event Timeline)
- SVG viewBox="0 0 300 160" with boundary, halfway line, center circle, penalty areas
- Cyan dots (Team A), emerald dots (Team B), dashed red defensive line, white ball marker

### 4.6 VideoCanvas (Live Workspace, Offside Review, Event Timeline)
- Full-bleed img/video background + CSS perspective grid overlay + absolute-positioned HUD children + gradient vignette

### 4.7 PlayerTrackingBox (Live Workspace)
- 4-corner reticle spans + animated centroid pip + floating telemetry tag

### 4.8 LaserPlaneOverlay (Offside Review)
- Vertical 2px bar + neon box-shadow + floating player tag + ground foot contact ellipse

### 4.9 TransportControls / ScrubberTrack (Live Workspace, Event Timeline)
- Custom range input with neon green thumb, event stamp pins, playhead needle, play/pause/step buttons, speed selector

### 4.10 EventCard (Event Timeline)
- Active: border-2 border-primary-fixed-dim + laser-glow-emerald
- Inactive: border border-outline-variant/30 + hover
- Contains: timestamp mono badge | event type badge | AI verdict badge | player row | 4-col stat bento | AI explanation

### 4.11 PipelineStageCard (Ingestion)
- h-36, progress bar at bottom. States: Complete (green border 100%) / Active (cyan border, animated %) / Pending (grey opacity-60)

### 4.12 MatchSessionCard (Ingestion)
- Media header h-48 + status overlay + VAR alert badge | body: title + venue + mini telemetry grid | CTA button

### 4.13 CameraAngleSwitcher
- Horizontal button group. Active: bg-primary-container text-on-primary. Inactive: text-on-surface hover:bg-surface-container-high

### 4.14 FilterChipRow (Event Timeline)
- Horizontal overflow-x-auto rounded-full pills. Active: bg-surface-container-high font-semibold

---

## 5. Design System / Tokens

### 5.1 Fonts (Google Fonts CDN)

| Role | Font | Weights |
|---|---|---|
| Display / Headlines | **Space Grotesk** | 500, 600, 700 |
| Body / UI copy | **Inter** | 300, 400, 500, 600, 700 |
| Telemetry / Metrics | **JetBrains Mono** | 400, 500, 600, 700 |
| Icons | **Material Symbols Outlined** (variable) | 100â€“700, FILL 0â€“1 |

### 5.2 Typography Scale

| Token | Size | Line-height | Letter-spacing | Weight | Font |
|---|---|---|---|---|---|
| display-xl | 48px | 52px | -0.03em | 700 | Space Grotesk |
| display-xl-mobile | 32px | 38px | -0.02em | 700 | Space Grotesk |
| headline-lg | 30px | 36px | -0.02em | 600 | Space Grotesk |
| headline-lg-mobile | 22px | 28px | -0.01em | 600 | Space Grotesk |
| headline-md | 20px | 26px | -0.01em | 600 | Space Grotesk |
| headline-sm | 16px | 22px | 0 | 600 | Space Grotesk |
| body-lg | 15px | 22px | -0.005em | 400 | Inter |
| body-md | 13px | 18px | 0 | 400 | Inter |
| body-sm | 11px | 16px | 0.01em | 400 | Inter |
| label-lg | 13px | 18px | 0.02em | 500 | JetBrains Mono |
| label-md | 11px | 14px | 0.04em | 500 | JetBrains Mono |
| label-sm | 9px | 12px | 0.06em | 600 | JetBrains Mono |

### 5.3 Color Palette (Semantic tokens)

**Surface tier (dark canvas)**

| Token | Hex | Role |
|---|---|---|
| surface-container-lowest | #0a0e14 | Deepest pitch black, video BG |
| surface-container-low | #181c22 | Nav bar, cards |
| surface-container | #1c2026 | Mid-tier cards |
| surface-container-high | #262a31 | Hover states, toggled chips |
| surface-container-highest | #31353c | Tooltips, highest elevation |
| surface-bright | #353940 | High contrast surface |
| surface / background | #10141a | Page background |
| outline-variant | #3b4b3d | Dividers, hairline borders |
| outline | #849585 | Muted borders |
| on-surface | #dfe2eb | Primary text |
| on-surface-variant | #b9cbb9 | Secondary text, muted labels |

**Accent palette**

| Token | Hex | Role |
|---|---|---|
| primary-container | #00ff88 | Electric Emerald â€” primary CTA, goal events, onside |
| primary-fixed-dim | #00e479 | Primary active state, playhead, tracking confirmed |
| primary-fixed | #60ff99 | Lighter emerald variant |
| on-primary-container | #007139 | Text on emerald bg |
| secondary-fixed-dim | #00daf3 | Laser Cyan â€” ball tracking, secondary actions, attacker line |
| secondary-container | #00e3fd | Cyan container |
| error | #ffb4ab | Error text / review amber |
| error-container | #93000a | Laser Crimson BG â€” offside line, foul events, red cards |
| on-error-container | #ffdad6 | Text on crimson bg |
| tertiary-fixed-dim | #c0c1ff | Ultra Violet â€” neural confidence, AI metrics |

### 5.4 Border Radius

| Token | Value | Use |
|---|---|---|
| DEFAULT | 0.125rem (2px) | Micro elements, chips |
| lg | 0.25rem (4px) | Cards, video corners, event blocks |
| xl | 0.5rem (8px) | HUD panels, modals |
| full | 0.75rem (12px) | Pills, nav tabs, status badges |

> **Inconsistency:** DESIGN.md defines `full: 9999px` but all Tailwind configs define `full: 0.75rem`. Resolve on migration.

### 5.5 Spacing Tokens

| Token | Value |
|---|---|
| space-xs | 0.25rem (4px) |
| space-sm | 0.5rem (8px) |
| space-md / gutter | 0.75rem (12px) |
| space-lg / margin | 1rem (16px) |
| space-xl | 1.5rem (24px) |

### 5.6 Custom CSS Classes (cross-screen)

| Class | Definition | Used in |
|---|---|---|
| .laser-plane-red | Gradient + red box-shadow glow | Offside Review |
| .laser-plane-cyan | Gradient + cyan box-shadow glow | Offside Review |
| .laser-line-green | Green box-shadow glow | Offside Review |
| .glow-cyan | box-shadow: 0 0 16px rgba(0,218,243,0.4) | Live Workspace |
| .glow-emerald | box-shadow: 0 0 16px rgba(0,228,121,0.4) | Live Workspace |
| .hud-scanner | Animated gradient sweep | Live Workspace |
| .timeline-scrub-bar | Custom range input thumb (neon green pill) | Live Workspace, Timeline |
| .hud-grid-pattern | 24px grid overlay | Timeline, Ingestion |
| .laser-glow-emerald | Green glow variant | Timeline, Player Analytics |
| .laser-glow-crimson | Red glow variant | Timeline |
| .laser-grid | 20px grid | Match Summary |
| .telemetry-grid | 24px grid | Player Analytics |
| .radar-pitch | Radial gradient + grid | Player Analytics |
| .tactical-grid-bg | 24px grid | Formation Radar |
| .scanline | Animated scan gradient | Formation Radar |
| .animate-pulse-subtle | Custom keyframe (opacity 1 to 0.4) | Ingestion |

---

## 6. Navigation Relationships

```
[Ingestion / Dashboard] â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ (Entry point â€” no top nav link)
         |
         +-- "Launch Workspace" --> [Live Workspace] <------+
                                           |                |
                            +--------------+----------------+
                            |              |                |
                     [Offside   [Formation   [Event    [Player   [Match
                     Review]    & Radar]    Timeline] Analytics] Summary]
                            |              |                |         |
                            +--------------+----------------+---------+
                                       (All linked via top nav)
```

All `href` values are `#` â€” non-functional stubs. Active state is hardcoded per screen, not driven by routing.

---

## 7. Required Frontend Architecture

### 7.1 Recommended Stack

| Layer | Recommendation | Rationale |
|---|---|---|
| Framework | Next.js 14+ (App Router) or Vite + React | Component reuse, routing, future SSR |
| Styling | Tailwind CSS v3 (local install) with shared custom config | Already used; extract shared config |
| State | Zustand or React Context | Match session, playback state, selected player |
| Routing | Next.js App Router or React Router v6 | 6 main routes + dynamic match session IDs |
| Video | HTML5 video / WebRTC | Replace static img stubs |
| SVG Rendering | Inline SVG / D3.js (pitch radar) | Dynamic player positions |
| Real-time | WebSocket / Socket.io | Live telemetry, match clock |
| Charts | Recharts or Visx | Sprint histograms, xG timelines |

### 7.2 Proposed Route Structure

```
/                                        Redirect to /sessions
/sessions                                Ingestion / Dashboard (session picker)
/sessions/[matchId]                      Live Analysis Workspace
/sessions/[matchId]/offside-review       VAR Offside Review
/sessions/[matchId]/formation            Formation & Tactical Radar
/sessions/[matchId]/timeline             Event Timeline & Incident Scrubber
/sessions/[matchId]/players              Player Analytics & Biometrics
/sessions/[matchId]/summary              Match Summary & VAR Audit Dossier
```

### 7.3 Proposed Component File Structure

```
src/
  components/
    layout/
      TopNavBar.tsx              # Shared across all 6 screens
      MatchStatusBar.tsx         # Live Workspace + Offside Review
    video/
      VideoCanvas.tsx            # Full-bleed video stage
      PlayerTrackingBox.tsx      # CV bounding box + telemetry tag
      BallTracker.tsx            # Crosshair + trajectory arc
      LaserPlaneOverlay.tsx      # Offside plane (red/cyan)
    controls/
      TransportControls.tsx      # Play/Pause/Step + speed
      ScrubberTrack.tsx          # Range input + event pins
      CameraAngleSwitcher.tsx
    radar/
      PitchSVGRadar.tsx          # SVG pitch map with player dots
    telemetry/
      BentoTelemetryCard.tsx
      TelemetryChip.tsx
      PlayerTelemetryCard.tsx
    events/
      EventCard.tsx              # Incident card with AI verdict
      FilterChipRow.tsx
      MultiTrackTimeline.tsx     # 5-track event timeline
    pipeline/
      PipelineStageCard.tsx
      MatchSessionCard.tsx
    ui/
      StatusBadge.tsx
      LaserGlowBox.tsx
      AnimatedPulse.tsx
  pages/ (or app/)
    sessions/
      index.tsx                  # Ingestion/Dashboard
      [matchId]/
        index.tsx                # Live Workspace
        offside-review.tsx
        formation.tsx
        timeline.tsx
        players.tsx
        summary.tsx
  styles/
    globals.css                  # Base layer, scrollbar, custom keyframes
    tailwind.config.ts           # Extracted shared design tokens
  lib/
    mockData/                    # All static data (see Section 8)
    api/                         # API client stubs (see Section 9)
  types/
    match.ts
    player.ts
    event.ts
    telemetry.ts
```

---

## 8. Mock / Static Data That Needs Replacement

### 8.1 Match Context (global â€” hardcoded across all screens)

```typescript
const mockMatch = {
  id: "UCL-2024-MCI-RMA-F",
  homeTeam: { code: "MCI", name: "Manchester City" },
  awayTeam: { code: "RMA", name: "Real Madrid" },
  score: { home: 2, away: 1 },
  clock: "67:24", period: "2H",
  competition: "UEFA Champions League", venue: "Etihad Stadium",
  status: "LIVE", feedSpec: "4K RAW 120FPS", latency: "12ms",
}
```

### 8.2 AI CV System Metrics

```typescript
const mockCVState = {
  engineVersion: "REVI-ENGINE 4.2",
  aiConfidence: 92.4, totalFrames: 162000, currentFrame: 121418,
  timecode: "01:07:24.482", inferencePeriodMs: 14.2,
  gpuClusterLoad: 74, gpuNodes: "8x H100",
  opticalCalib: "0.08mm", trackingConfidence: 94.2,
  skeletalConf: 99.4, ballVelocityKph: 86.4,
}
```

### 8.3 Offside Review Incident

```typescript
const mockOffsideIncident = {
  incidentId: "VAR-OFF-67-001", frameId: 194821,
  aiEstimation: "ONSIDE", marginMeters: 0.142, uncertainty: 0.018,
  aiConfidence: 92.4,
  attacker: { jersey: 19, name: "Mason Mount", axisMeters: 34.08,
    centroid: { x: 34.08, y: -8.12, z: 1.42 } },
  defender: { jersey: 15, name: "Eric Dier", axisMeters: 34.22,
    centroid: { x: 34.22, y: -7.88, z: 0.12 } },
  ballContact: { frameId: 194821, ballSpeedKph: 94.2, confirmed: true },
}
```

### 8.4 Match Events (13 hardcoded events across screens)

Events span minutes 12, 17, 22, 28, 34, 39, 44, 46, 53, 58, 61, 66, 67 covering:
GOAL | YELLOW_CARD | PENALTY_RESCINDED | OFFSIDE | SUBSTITUTION | HIGH_DANGER_FOUL | GOAL_UNDER_REVIEW

Key active incident: **Mount #19 GOAL UNDER REVIEW at 67:24, Frame 121,418, xG 0.74**

### 8.5 Players (6 hardcoded across screens)

- #19 Mason Mount â€” Chelsea FC / Man City â€” Attacking Midfield â€” aiConf 98.8%
- #15 Eric Dier â€” Tottenham Hotspur â€” Centre-Back â€” aiConf 99.2%
- #17 Kevin De Bruyne â€” Manchester City / Belgium
- #09 Erling Haaland â€” Manchester City / Norway
- #07 Vinicius Jr. â€” Real Madrid / Brazil
- #10 Luka Modric â€” Real Madrid / Croatia

### 8.6 Match Sessions (3 hardcoded on ingestion screen)

- Manchester City vs Real Madrid â€” UCL Semi-Final â€” READY (14 VAR alerts)
- Bayern Munich vs Arsenal â€” UCL Quarter-Final â€” ARCHIVED (2h ago)
- Inter vs Atletico â€” UCL R16 â€” PROCESSING 68% (ETA 4:18m)

### 8.7 Neural Pipeline Stages (6 hardcoded stages)

Stage 1 Ingestion: COMPLETE 100% (162,000 frames)  
Stage 2 DeepLab: COMPLETE 100% (22 centroids)  
Stage 3 YOLOv9: ACTIVE 88% (104.2 km/h)  
Stage 4 Jersey OCR: PENDING 0%  
Stage 5 Homography 3D: PENDING 0%  
Stage 6 VAR Engine: PENDING 0%

---

## 9. Required API Boundaries

### 9.1 Match Session API

| Endpoint | Method | Purpose |
|---|---|---|
| GET /api/sessions | GET | List all match sessions |
| GET /api/sessions/:matchId | GET | Single match metadata and status |
| POST /api/sessions | POST | Ingest new match (upload / RTSP link) |
| GET /api/sessions/:matchId/pipeline | GET | Pipeline stage progress |

### 9.2 Live Telemetry API (WebSocket)

| Channel | Direction | Payload |
|---|---|---|
| ws://host/match/:matchId/telemetry | Server to Client | Player positions, ball XYZ, frame number, timecode |
| ws://host/match/:matchId/events | Server to Client | New match event from CV engine |
| ws://host/match/:matchId/var-alert | Server to Client | VAR alert push |

### 9.3 CV Inference API

| Endpoint | Purpose |
|---|---|
| GET /api/matches/:id/frames/:frameId | Single frame with CV annotations |
| GET /api/matches/:id/players | All tracked players with latest positions |
| GET /api/matches/:id/players/:playerId | Individual player full biometrics |
| GET /api/matches/:id/ball | Ball tracking state at current frame |
| POST /api/matches/:id/offside-check | Trigger SAOT homography offside computation |
| GET /api/matches/:id/offside-check/:checkId | Get offside check result |

### 9.4 Events and Timeline API

| Endpoint | Purpose |
|---|---|
| GET /api/matches/:id/events | All match events (filterable by type) |
| GET /api/matches/:id/events/:eventId | Single event with full telemetry |
| PATCH /api/matches/:id/events/:eventId | Update official VAR decision |

### 9.5 Formation and Tactical API

| Endpoint | Purpose |
|---|---|
| GET /api/matches/:id/formations | Team formation snapshots |
| GET /api/matches/:id/tactical/zones | Pressure zones, compactness metrics |
| GET /api/matches/:id/tactical/heatmap/:playerId | Player pitch heatmap |

### 9.6 Export and Audit API

| Endpoint | Purpose |
|---|---|
| POST /api/matches/:id/export | Export dossier (JSON / VAR3D) |
| GET /api/matches/:id/audit | Full VAR audit log |
| POST /api/matches/:id/sign-off | Official VAR sign-off |

### 9.7 Video and Camera API

| Endpoint | Purpose |
|---|---|
| GET /api/matches/:id/cameras | Available camera angles |
| GET /api/matches/:id/cameras/:camId/stream | WebRTC / HLS stream URL |
| GET /api/matches/:id/cameras/:camId/frame/:frameId | Frame thumbnail |

---

## 10. Interactive Elements Requiring Real Backend Data

| Screen | Element | Currently mocked | Backend requirement |
|---|---|---|---|
| Live Workspace | Play/Pause scrubber | setInterval faking frame count | WebSocket stream / HLS video seek |
| Live Workspace | Player bounding boxes | Hardcoded absolute position % | CV model frame-accurate bbox coordinates |
| Live Workspace | Ball tracker | Static position on image | CV model real-time ball XYZ |
| Live Workspace | Trajectory SVG arc | Hardcoded SVG path | CV model ball trajectory vector |
| Live Workspace | Tracking confidence 94.2% | Static string | CV engine live confidence metric |
| Live Workspace | Timecode + frame counter | Math on scrubber value | True broadcast SMPTE timecode |
| Live Workspace | Pitch radar player dots | Hardcoded SVG cx/cy | CV model player centroid positions |
| Offside Review | Laser planes | Hardcoded left: 53.8% etc. | Homography reprojection coordinates |
| Offside Review | Margin delta +14.2cm | Hardcoded | SAOT offside computation result |
| Offside Review | Sub-frame stepper | Button flash only | Frame-accurate video seek API |
| Offside Review | Send AI Offside Dossier button | No action | POST /api/matches/:id/offside-check |
| Formation Radar | Player dot positions | Hardcoded SVG coordinates | Live player tracking normalized pitch coords |
| Event Timeline | Timeline event pins | Hardcoded left: X% | Match events API |
| Event Timeline | Filter chip counts | Hardcoded e.g. "VAR Interventions (4)" | GET /events?type=VAR aggregation |
| Event Timeline | Jump to Broadcast button | No action | Video seek + camera sync |
| Player Analytics | Player stats | Hardcoded per player | GET /players/:id biometric API |
| Player Analytics | Heatmap | Static SVG | Spatial tracking data aggregation |
| Player Analytics | Skeletal confidence | Static 98.8% | Real-time pose estimation output |
| Match Summary | VAR decision table | Hardcoded rows | GET /audit full match log |
| Match Summary | Official Sign-Off button | No action | POST /sign-off with referee auth |
| Match Summary | Export Telemetry button | No action | POST /export download trigger |
| Ingestion | Pipeline stage progress | Static 100%/88%/0% | GET /pipeline polling or WebSocket |
| Ingestion | Launch Workspace button | No routing | Navigate to /sessions/:matchId |
| Ingestion | Upload Match Video | No file input | POST /sessions multipart upload |
| Ingestion | Connect Live Feed | Hardcoded IP 192.168.10.88 | RTSP connection form |
| All screens | Avatar image | lh3.googleusercontent.com | Auth service / user profile API |
| All screens | Navigation links | href="#" | React Router / Next.js Link |
| All screens | Broadcast Stream CTA | No action | WebRTC / HLS stream handler |

---

## 11. External Dependencies

### 11.1 CDN Dependencies (currently used)

| Resource | Current | Should migrate to |
|---|---|---|
| Tailwind CSS | cdn.tailwindcss.com | npm install tailwindcss + PostCSS pipeline |
| Google Fonts | fonts.googleapis.com | Keep CDN or self-host with next/font |
| Material Symbols | fonts.googleapis.com (variable icon font) | Keep CDN or @material-symbols/font-700 |
| AI Images | lh3.googleusercontent.com | Replace with real broadcast frames or local assets |

### 11.2 npm Dependencies to Install

```json
{
  "dependencies": {
    "react": "^18",
    "react-dom": "^18",
    "next": "^14",
    "tailwindcss": "^3",
    "postcss": "^8",
    "autoprefixer": "^10",
    "@tailwindcss/forms": "^0.5",
    "clsx": "^2",
    "framer-motion": "^11",
    "zustand": "^4",
    "socket.io-client": "^4",
    "hls.js": "^1",
    "recharts": "^2"
  },
  "devDependencies": {
    "typescript": "^5",
    "@types/react": "^18",
    "@types/node": "^20"
  }
}
```

---

## 12. Inconsistencies Between Screens

| # | Issue | Screens affected | Resolution |
|---|---|---|---|
| 1 | Brand icon varies: troubleshoot / videocam / radar | Offside Review, Live Workspace, Formation Radar | Pick one canonical icon â€” recommend `sensors` |
| 2 | Version badge varies: REVI-ENGINE 4.2, CV INFERENCE v4.2, NEURAL HUD 4.2, TACTICAL v4.2, AUDIT-OS v4.8, OPT-HUD v4.8 | All screens | Single VERSION constant from build config |
| 3 | Nav icon usage inconsistent: some tabs have icons, some don't | Live Workspace vs others | Standardise â€” all icons or no icons |
| 4 | Two folders with identical HTML (Ingestion = VAR Ops) | Both ingestion folders | One canonical Sessions/Dashboard screen |
| 5 | borderRadius.full mismatch: DESIGN.md says 9999px, Tailwind configs say 0.75rem | All | Resolve to 9999px or keep 0.75rem |
| 6 | Spacing tokens `margin` and `space-lg` are identical (1rem) | All | Collapse to one token |
| 7 | Duplicate Material Symbols link tag appears twice in head | All | Single link tag |
| 8 | visionvar_pitch_intelligence folder has only DESIGN.md, no HTML or PNG | That folder | Merge DESIGN.md into project docs |
| 9 | Player club affiliations inconsistent: Mount shown as "Chelsea FC" and "Man City" | Live Workspace vs Event Timeline | Normalise player data |
| 10 | ultra_high_definition_broadcast has only a PNG, no HTML | That folder | Treat as splash/loading reference only |
| 11 | Match clock hardcoded at 67:24 everywhere but described as LIVE | All live screens | Replace with real WebSocket clock |
| 12 | Material Symbols font variation opsz differs: 20 vs 24 | Ingestion vs Player Analytics | Standardise to opsz 24 |
| 13 | "Export Telemetry" button uses different icons: settings / upload_file / file_download / download | All | Standardise to file_download |
| 14 | rounded-lg / rounded-xl applied ad-hoc rather than via design token classes | All | Use design token class names consistently |

---

## 13. Recommended Migration Path

### Phase 0 â€” Prerequisites (1â€“2 days)
1. Initialize Next.js 14 project with TypeScript in `VisionVAR/`
2. Install Tailwind CSS locally; copy design tokens from any screen's tailwind.config into `tailwind.config.ts`
3. Set up Google Fonts via `next/font/google` (Space Grotesk, Inter, JetBrains Mono)
4. Set up Material Symbols as CDN link in `layout.tsx`
5. Create `src/styles/globals.css` with all custom CSS classes: laser glows, scanner, grid patterns, scrollbar, range slider
6. Create `src/types/` TypeScript interfaces for all mock data models

### Phase 1 â€” Shared Components (2â€“3 days)
1. Build TopNavBar with active route detection via `usePathname()`
2. Build BentoTelemetryCard, TelemetryChip, StatusBadge, CameraAngleSwitcher
3. Build PitchSVGRadar as a configurable component
4. Build TransportControls + ScrubberTrack with mock data props
5. Create mock data JSON files for all screens

### Phase 2 â€” Screen-by-Screen Migration (5â€“7 days)
Convert each HTML file to a React page, preserving pixel-accurate layout. All data from mock JSON at this stage.

1. Sessions / Dashboard (`/sessions`) â€” pipeline cards + session grid
2. Live Workspace (`/sessions/[matchId]`) â€” video stage + CV overlays + bottom bento
3. Offside Review (`/sessions/[matchId]/offside-review`) â€” freeze frame + laser planes + stepper
4. Formation & Radar (`/sessions/[matchId]/formation`) â€” SVG pitch + sidebar panels
5. Event Timeline (`/sessions/[matchId]/timeline`) â€” multi-track + event cards + inspector
6. Player Analytics (`/sessions/[matchId]/players`) â€” roster + dossier + heatmap
7. Match Summary (`/sessions/[matchId]/summary`) â€” audit table + scorecard + export

### Phase 3 â€” Wire Up Navigation (1 day)
1. Replace all `href="#"` with Next.js `Link` components
2. Active state via `usePathname()`
3. Persist matchId param across all sub-routes

### Phase 4 â€” Real Video Integration (variable)
1. Replace static img broadcast stills with `video` element (HLS.js) or WebRTC stream
2. Implement play/pause/step with real video events
3. Sync scrubber with video `currentTime`

### Phase 5 â€” Live CV Data Integration (variable)
1. Replace all mock telemetry with WebSocket subscriptions
2. Wire player bounding boxes to real normalized bbox coordinates
3. Wire pitch radar dots to live player centroids
4. Implement real offside plane computation

### Phase 6 â€” Backend API Integration (variable)
1. Replace mock data arrays with fetch/axios calls to backend endpoints
2. Implement session creation (file upload / RTSP connection)
3. Implement VAR audit sign-off
4. Implement telemetry export

---

## 14. Source Assets Reference

| Asset | Location | Status |
|---|---|---|
| All screen HTML files | stitch_â€¦/ subdirectories | Preserved â€” source of truth |
| All screen PNGs | stitch_â€¦/screen.png | Preserved â€” visual reference |
| DESIGN.md (design system) | visionvar_pitch_intelligence/DESIGN.md | Preserved |
| AI-generated broadcast images | lh3.googleusercontent.com URLs | External CDN â€” may expire; download locally |

> **All Stitch files are preserved. Do not modify or delete them.**

---

*End of STITCH_ANALYSIS.md â€” VisionVAR Technical Analysis v1.0*
