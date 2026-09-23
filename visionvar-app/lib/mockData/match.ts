import type { MatchContext, CVState, MatchSession, PipelineStage } from '@/types';

export const MATCH_ID = 'UCL-2024-MCI-RMA-F';

export const mockMatch: MatchContext = {
  id: MATCH_ID,
  homeTeam: { code: 'MCI', name: 'Manchester City' },
  awayTeam: { code: 'RMA', name: 'Real Madrid' },
  score: { home: 2, away: 1 },
  clock: '67:24',
  period: '2H',
  competition: 'UEFA Champions League',
  venue: 'Etihad Stadium',
  status: 'LIVE',
  feedSpec: '4K RAW 120FPS',
  latencyMs: 12,
};

export const mockCVState: CVState = {
  engineVersion: 'CV INFERENCE v4.2',
  aiConfidence: 92.4,
  pitchMapping: '12-POINT REPROJECTION',
  totalFrames: 162000,
  currentFrame: 121418,
  timecode: '01:07:24.482',
  inferencePeriodMs: 14.2,
  gpuClusterLoad: 74,
  gpuNodes: '8x H100',
  opticalCalib: '±0.08mm',
  trackingConfidence: 94.2,
  skeletalConf: 99.4,
  ballVisibility: 'HIGH',
  ballVelocityKph: 86.4,
};

export const mockCameras = [
  { id: 'main', label: 'Main Broadcast' },
  { id: 'end-zone', label: 'High End-Zone' },
  { id: 'tactical', label: 'Tactical 16m' },
  { id: 'reverse', label: 'Reverse Angle' },
];

export const mockPipelineStages: PipelineStage[] = [
  { stage: 1, label: 'Ingestion & Extraction', status: 'COMPLETE', progress: 100, detail: '162,000 frames sliced' },
  { stage: 2, label: 'DeepLab Player Detect', status: 'COMPLETE', progress: 100, detail: '22 centroids identified' },
  { stage: 3, label: 'Ball Tracking (YOLOv9)', status: 'ACTIVE', progress: 88, detail: 'Velocity: 104.2 km/h' },
  { stage: 4, label: 'Jersey Optical OCR', status: 'PENDING', progress: 0, detail: 'Awaiting Ball Anchor' },
  { stage: 5, label: 'Homography 3D Mesh', status: 'PENDING', progress: 0, detail: 'Pitch projective matrix' },
  { stage: 6, label: 'Synthetic VAR Engine', status: 'PENDING', progress: 0, detail: 'Offside line computation' },
];

export const AVATAR_URL =
  'https://lh3.googleusercontent.com/aida-public/AB6AXuBNcOI0bMmgCNP6cIWu5wdIB1MYxzDJkyxoh2FQDPirL_gcXRM3QQRiEdYMdB2fJpjf8qBm2im5Vx-dLkrAN7YXwu06rgZk5Wa1V6c0Q7LPatuaTMCncbsPVGRR8u06GOENrQfsVXGqlONHQxe5jFSpopreODND_RjceSGGajxu_bmLLkrw9gPtT1Fxj0hs1izF7Q14YFMg_bXAf-o0iViEWHsYNZQ6L-pkp-Xh93CkJnvhTdMTf3aQ';

export const mockSessions: MatchSession[] = [
  {
    id: 'UCL-2024-MCI-RMA-F',
    homeTeam: 'Manchester City',
    awayTeam: 'Real Madrid',
    competition: 'UCL Semi-Final',
    venue: 'Etihad Stadium',
    status: 'READY',
    imageUrl:
      'https://lh3.googleusercontent.com/aida-public/AB6AXuBm42jvQ9ReERba-4rgVJF1S6wBtM1-pHEeCZnV-FroGWllwMj3rz_49xQwDcbyE8QQb5Q5NIfgkC2iGwiNxmBJCNhTBjzQPPWNkG3lVGFnh5H-vJ65VCmJ118_LIUg3rJaMMJm9MQ0TfvIapTS8IX761nApI_2DfkN6xcG00zf62Bt1SAOcXIVkXmup5L2pTWu7CxFLyJtxR6OumBidV-LpImLSzrbAIqcxpw7Ht8HlB7l60_kadSH',
    varAlerts: 14,
    offsideChecks: 9,
    penaltyRadar: 3,
    redCardEval: 2,
    archivedMinutesAgo: 12,
    cameraSources: '4-Camera Synchronized VAR feed',
  },
  {
    id: 'UCL-2024-BAY-ARS-QF',
    homeTeam: 'Bayern Munich',
    awayTeam: 'Arsenal',
    competition: 'UCL Quarter-Final',
    venue: 'Allianz Arena',
    status: 'ARCHIVED',
    imageUrl:
      'https://lh3.googleusercontent.com/aida-public/AB6AXuDJKQcO46lczmV3uvMU3eNjMXPlcQaLNVIy5v2HBkqikgMCwf6KhsgsyogANRwEkMf5x11HrcJJdV4BnNkD9dPbihenmzIpHLHidbb-ovD8O76Q4C-mPCUZGxJ33GAss9Mjrw8JLVmVZwyjsPSxVdj8zCBLBzvRRZEhM5OXD9KLQylS8sm6zdYYug_jmDyCiqF0oshIklIU6vaDKCnsWI57iSX85ARI2xLRW4H2QU0Xv3RFgTpFGzio',
    offsideChecks: 16,
    goalVerify: 4,
    avgOverturnSeconds: 22.4,
    archivedHoursAgo: 2,
  },
  {
    id: 'UCL-2024-INT-ATL-R16',
    homeTeam: 'Inter',
    awayTeam: 'Atletico',
    competition: 'UCL R16',
    venue: 'San Siro',
    status: 'PROCESSING',
    imageUrl:
      'https://lh3.googleusercontent.com/aida-public/AB6AXuAUOwdgdpJSGJ83a9o3_-3NmJUWherZh8ZWG0VMaD_FkPJ8zNvikcJNZevxAcIFMsQcI1ucaEx7k4BTnW80MpKd6qXmSXGrNFoOYXbuj7CTjGoiJ3DvroCN54EpKNGDOyRAdCxgEQgrWy-UX02BKq8_kFTsZ9ar0xtnBNzisJuh3SpPzYtyEIiPi8RUpBUTQnNRcq6HrBrExXr52HOQhS3AFx2L7QG8U2ylgamelzNLUzg9VLwat5i1',
    processingPercent: 68,
    etaMinutes: 4.3,
  },
];
