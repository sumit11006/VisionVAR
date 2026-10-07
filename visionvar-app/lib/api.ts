// VisionVAR Frontend API Client
// Connects Next.js frontend to FastAPI backend running on http://localhost:8000

import type { MatchContext, MatchEvent, MatchSession } from '@/types';

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
export const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws/analysis';

export interface HealthStatus {
  status: string;
  version: string;
  service: string;
  database: string;
  cv_pipeline: string;
}

export interface PlayerTelemetryData {
  player_id: string;
  match_id: string;
  name: string;
  jersey: number;
  team: string;
  stats: {
    distanceKm: number;
    sprints: number;
    topSpeedKph: number;
    avgVelocityKph: number;
  };
  centroid: { x: number; y: number; z: number };
  pitch_coordinates: { pitch_x: number; pitch_y: number };
  ai_confidence: number;
  skeletal_lock_status: string;
  instantaneous_speed_kph: number;
  acceleration_ms2: number;
  stamina_index: number;
  timecode: string;
}

export interface CVNotImplementedResult {
  status: 'not_implemented';
  module: string;
  match_id: string;
  message: string;
  contract_specification?: Record<string, unknown>;
  data?: Record<string, unknown>;
}

// ─── Real Detection Schemas ───────────────────────────────────────────────────

export interface BoundingBox {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

export interface DetectionItem {
  class: 'player' | 'ball' | string;
  confidence: number;
  bbox: BoundingBox;
}

export interface TrackedItem {
  track_id: number;
  class: 'player' | 'ball' | string;
  confidence: number;
  bbox: BoundingBox;
  center: { x: number; y: number };
  frame: number;
  timestamp: number;
  state: string;
  team?: string;
  team_confidence?: number;
  pitch_position?: { x: number; y: number };
  mapping_status?: string;
  movement_trail?: [number, number][];
}

export interface BallState {
  track_id: number;
  state: 'tracked' | 'lost' | 'reacquired' | 'unavailable';
  image_position?: { x: number; y: number } | null;
  pitch_position?: { x: number; y: number } | null;
  confidence?: number;
  bbox?: number[] | null;
  movement_trail?: [number, number][];
}

export interface OffsideCandidate {
  status: 'candidate' | 'insufficient_evidence';
  reason?: string;
  ball_contact?: {
    state: string;
    confidence: number;
    evidence?: any;
  };
  team_a_attacking_dir?: string;
  team_b_attacking_dir?: string;
  offside_line_against_a?: {
    status: string;
    x: number;
    defender_id?: number;
  };
  offside_line_against_b?: {
    status: string;
    x: number;
    defender_id?: number;
  };
  players?: {
    track_id: number;
    team: string;
    pitch_x: number;
    status: string;
  }[];
  ai_assessment?: string;
  evidence?: string;
}

export interface FrameTrackingMessage {
  type: 'frame_tracking';
  session_id: string;
  frame: number;
  timestamp: number;
  tracked_items: TrackedItem[];
  formation?: {
    team_a?: string;
    team_b?: string;
    confidence?: number;
  };
  ball?: BallState;
  offside?: OffsideCandidate;
  inference_time_ms?: number;
  tracking_time_ms?: number;
  total_frames?: number;
  fps?: number;
  duration_seconds?: number;
  width?: number;
  height?: number;
}

export interface ProcessingStatusMessage {
  type: 'processing_status';
  session_id: string;
  status: 'processing' | 'completed' | 'error';
  progress: number;
  current_frame?: number;
  total_frames?: number;
  fps?: number;
  duration_seconds?: number;
  resolution?: string;
  width?: number;
  height?: number;
  message?: string;
}

// ─── REST Fetchers ─────────────────────────────────────────────────────────────

export async function fetchHealth(): Promise<HealthStatus> {
  const res = await fetch(`${API_BASE_URL}/health`);
  if (!res.ok) throw new Error(`Health check failed: ${res.statusText}`);
  return res.json();
}

export async function fetchSessions(): Promise<MatchSession[]> {
  const res = await fetch(`${API_BASE_URL}/analysis/sessions`);
  if (!res.ok) throw new Error(`Failed to fetch sessions: ${res.statusText}`);
  return res.json();
}

export async function fetchSession(sessionId: string): Promise<MatchSession> {
  const res = await fetch(`${API_BASE_URL}/analysis/sessions/${sessionId}`);
  if (!res.ok) throw new Error(`Failed to fetch session ${sessionId}: ${res.statusText}`);
  return res.json();
}

export async function fetchMatch(matchId: string): Promise<MatchContext> {
  const res = await fetch(`${API_BASE_URL}/matches/${matchId}`);
  if (!res.ok) throw new Error(`Failed to fetch match ${matchId}: ${res.statusText}`);
  return res.json();
}

export async function fetchMatchEvents(matchId: string): Promise<MatchEvent[]> {
  const res = await fetch(`${API_BASE_URL}/matches/${matchId}/events`);
  if (!res.ok) throw new Error(`Failed to fetch events for match ${matchId}: ${res.statusText}`);
  const json = await res.json();
  return json.events;
}

export async function fetchPlayerTelemetry(matchId: string, playerId: string): Promise<PlayerTelemetryData> {
  const res = await fetch(`${API_BASE_URL}/matches/${matchId}/players/${playerId}/telemetry`);
  if (!res.ok) throw new Error(`Failed to fetch player telemetry for ${playerId}: ${res.statusText}`);
  return res.json();
}

export async function fetchMatchAnalytics(matchId: string) {
  const res = await fetch(`${API_BASE_URL}/matches/${matchId}/analytics`);
  if (!res.ok) throw new Error(`Failed to fetch match analytics for ${matchId}: ${res.statusText}`);
  return res.json();
}

export async function fetchMatchSummary(matchId: string) {
  const res = await fetch(`${API_BASE_URL}/matches/${matchId}/summary`);
  if (!res.ok) throw new Error(`Failed to fetch match summary for ${matchId}: ${res.statusText}`);
  return res.json();
}

export async function fetchFormation(matchId: string): Promise<CVNotImplementedResult> {
  const res = await fetch(`${API_BASE_URL}/matches/${matchId}/formation`);
  if (!res.ok) throw new Error(`Failed to fetch formation: ${res.statusText}`);
  return res.json();
}

export async function fetchOffside(matchId: string): Promise<CVNotImplementedResult> {
  const res = await fetch(`${API_BASE_URL}/matches/${matchId}/offside`);
  if (!res.ok) throw new Error(`Failed to fetch offside analysis: ${res.statusText}`);
  return res.json();
}

export async function fetchTrackingHistory(sessionId: string) {
  const res = await fetch(`${API_BASE_URL}/analysis/sessions/${sessionId}/tracking`);
  if (!res.ok) {
    if (res.status === 404) return null; // No tracking history yet
    throw new Error(`Failed to fetch tracking history: ${res.statusText}`);
  }
  return res.json();
}

export async function uploadVideo(file: File) {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_BASE_URL}/videos/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Upload failed' }));
    throw new Error(err.detail || 'Upload failed');
  }

  return res.json();
}

export async function startDetection(
  sessionId: string,
  payload?: { video_id?: string; frame_skip?: number; confidence_threshold?: number }
) {
  const res = await fetch(`${API_BASE_URL}/analysis/sessions/${sessionId}/detect`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload || {}),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to start detection' }));
    throw new Error(err.detail || 'Failed to start detection');
  }

  return res.json();
}

// ─── WebSocket Client ──────────────────────────────────────────────────────────

export function connectAnalysisWebSocket(
  sessionId: string,
  onMessage: (data: Record<string, unknown>) => void,
  onOpen?: () => void,
  onError?: (err: Event) => void
): WebSocket {
  const ws = new WebSocket(`${WS_BASE_URL}/${sessionId}`);

  ws.onopen = () => {
    if (onOpen) onOpen();
  };

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch {
      // Ignored non-json frames
    }
  };

  if (onError) {
    ws.onerror = onError;
  }

  return ws;
}
