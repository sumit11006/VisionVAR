// VisionVAR — All TypeScript types extracted from Stitch designs

// ─── Match ────────────────────────────────────────────────────────────────────

export interface Team {
  code: string;
  name: string;
}

export interface MatchContext {
  id: string;
  homeTeam: Team;
  awayTeam: Team;
  score: { home: number; away: number };
  clock: string;
  period: string;
  competition: string;
  venue: string;
  status: 'LIVE' | 'REVIEWING' | 'COMPLETE';
  feedSpec: string;
  latencyMs: number;
}

export interface CVState {
  engineVersion: string;
  aiConfidence: number;
  pitchMapping: string;
  totalFrames: number;
  currentFrame: number;
  timecode: string;
  inferencePeriodMs: number;
  gpuClusterLoad: number;
  gpuNodes: string;
  opticalCalib: string;
  trackingConfidence: number;
  skeletalConf: number;
  ballVisibility: string;
  ballVelocityKph: number;
}

// ─── Pipeline ─────────────────────────────────────────────────────────────────

export type PipelineStatus = 'COMPLETE' | 'ACTIVE' | 'PENDING';

export interface PipelineStage {
  stage: number;
  label: string;
  status: PipelineStatus;
  progress: number;
  detail: string;
}

// ─── Match Session ─────────────────────────────────────────────────────────────

export type SessionStatus = 'READY' | 'ARCHIVED' | 'PROCESSING';

export interface VideoMetadata {
  video_id: string;
  filename: string;
  fps: number;
  total_frames: number;
  duration_seconds: number;
  resolution: string;
  width: number;
  height: number;
}

export interface MatchSession {
  id: string;
  homeTeam: string;
  awayTeam: string;
  competition: string;
  venue: string;
  status: SessionStatus;
  imageUrl: string;
  varAlerts?: number;
  offsideChecks?: number;
  penaltyRadar?: number;
  redCardEval?: number;
  goalVerify?: number;
  avgOverturnSeconds?: number;
  archivedMinutesAgo?: number;
  archivedHoursAgo?: number;
  processingPercent?: number;
  etaMinutes?: number;
  cameraSources?: string;
  video_metadata?: VideoMetadata;
}

// ─── Events ────────────────────────────────────────────────────────────────────

export type EventType =
  | 'GOAL'
  | 'YELLOW_CARD'
  | 'RED_CARD'
  | 'OFFSIDE'
  | 'PENALTY_RESCINDED'
  | 'HIGH_DANGER_FOUL'
  | 'SUBSTITUTION'
  | 'GOAL_UNDER_REVIEW'
  | 'VAR_INTERVENTION'
  | 'BALL_CONTACT'
  | 'PASS_CANDIDATE'
  | 'POSSESSION_CANDIDATE'
  | 'BALL_RECOVERY_CANDIDATE'
  | 'TURNOVER_CANDIDATE'
  | 'OFFSIDE_CANDIDATE'
  | string;

export interface MatchEvent {
  id: string;
  minute: number;
  second: number;
  frameId: number;
  timecode: string;
  type: EventType;
  team: string;
  player: string | null;
  playerJersey?: number;
  playerTeam?: string;
  description?: string;
  aiVerdict: string | null;
  xg?: number | null;
  ballVelocityKph?: number;
  impactGForce?: number;
  saotMarginCm?: number;
  aiExplanation?: string;
  isActive?: boolean;
  status?: string;
  confidence?: number;
  metadata_json?: string;
}

// ─── Players ────────────────────────────────────────────────────────────────────

export interface PlayerStats {
  distanceKm: number;
  sprints: number;
  topSpeedKph: number;
  avgVelocityKph: number;
}

export interface Player {
  id: string;
  jersey: number;
  name: string;
  team: string;
  nationality: string;
  role: string;
  aiConfidence: number;
  skeletalLockStatus: string;
  stats: PlayerStats;
  centroid: { x: number; y: number; z: number };
  pitchX?: number; // normalized 0-300 for SVG
  pitchY?: number; // normalized 0-160 for SVG
}

// ─── Offside Incident ──────────────────────────────────────────────────────────

export interface OffsidePlayer {
  jersey: number;
  name: string;
  team: string;
  bodyPartDatum: string;
  axisMeters: number;
  velocityKph?: number;
  accelerationMs2?: number;
  bodyLeanAngle?: number;
  centroid: { x: number; y: number; z: number };
}

export interface OffsideIncident {
  incidentId: string;
  frameId: number;
  timecode: string;
  camera: string;
  aiEstimation: 'ONSIDE' | 'OFFSIDE';
  marginMeters: number;
  uncertaintyMeters: number;
  aiConfidence: number;
  attacker: OffsidePlayer;
  defender: OffsidePlayer;
  ballContact: {
    timecode: string;
    frameId: number;
    ballSpeedKph: number;
    confirmed: boolean;
  };
  cameraParams: { focal: string; aperture: string; distortion: string };
  refereeStatus: string;
  broadcastStatus: string;
  latencyToPitchMs: number;
}

// ─── Camera / Nav ──────────────────────────────────────────────────────────────

export interface Camera {
  id: string;
  label: string;
}

export type NavRoute =
  | 'workspace'
  | 'offside-review'
  | 'formation'
  | 'timeline'
  | 'players'
  | 'summary';
