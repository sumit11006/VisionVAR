import type { Player } from '@/types';

export const mockPlayers: Player[] = [
  {
    id: '849-19', jersey: 19, name: 'Mason Mount',
    team: 'Chelsea FC / Man City', nationality: 'ENG',
    role: 'Attacking Midfield',
    aiConfidence: 98.8, skeletalLockStatus: 'OK',
    stats: { distanceKm: 8.42, sprints: 19, topSpeedKph: 32.8, avgVelocityKph: 28.4 },
    centroid: { x: 34.08, y: -8.12, z: 1.42 },
    pitchX: 210, pitchY: 82,
  },
  {
    id: '849-15', jersey: 15, name: 'Eric Dier',
    team: 'Tottenham Hotspur', nationality: 'ENG',
    role: 'Centre-Back',
    aiConfidence: 99.2, skeletalLockStatus: 'OK',
    stats: { distanceKm: 7.20, sprints: 11, topSpeedKph: 28.4, avgVelocityKph: 21.6 },
    centroid: { x: 34.22, y: -7.88, z: 0.12 },
    pitchX: 220, pitchY: 95,
  },
  {
    id: '849-17', jersey: 17, name: 'Kevin De Bruyne',
    team: 'Manchester City', nationality: 'BEL',
    role: 'Central Midfield',
    aiConfidence: 97.6, skeletalLockStatus: 'OK',
    stats: { distanceKm: 9.14, sprints: 22, topSpeedKph: 30.2, avgVelocityKph: 26.8 },
    centroid: { x: 28.4, y: -4.2, z: 1.1 },
    pitchX: 115, pitchY: 80,
  },
  {
    id: '849-09', jersey: 9, name: 'Erling Haaland',
    team: 'Manchester City', nationality: 'NOR',
    role: 'Centre Forward',
    aiConfidence: 99.1, skeletalLockStatus: 'OK',
    stats: { distanceKm: 6.88, sprints: 28, topSpeedKph: 35.8, avgVelocityKph: 24.2 },
    centroid: { x: 38.6, y: -2.1, z: 1.8 },
    pitchX: 235, pitchY: 35,
  },
  {
    id: '849-07', jersey: 7, name: 'Vinícius Jr.',
    team: 'Real Madrid', nationality: 'BRA',
    role: 'Left Winger',
    aiConfidence: 98.4, skeletalLockStatus: 'OK',
    stats: { distanceKm: 8.96, sprints: 31, topSpeedKph: 36.4, avgVelocityKph: 27.6 },
    centroid: { x: 26.8, y: 14.2, z: 1.2 },
    pitchX: 170, pitchY: 50,
  },
  {
    id: '849-10', jersey: 10, name: 'Luka Modrić',
    team: 'Real Madrid', nationality: 'CRO',
    role: 'Central Midfield',
    aiConfidence: 96.8, skeletalLockStatus: 'OK',
    stats: { distanceKm: 10.2, sprints: 18, topSpeedKph: 27.4, avgVelocityKph: 23.8 },
    centroid: { x: 22.4, y: 1.8, z: 1.0 },
    pitchX: 165, pitchY: 80,
  },
];

// Team A (cyan) dots for pitch radar
export const teamACentroidsRadar = [
  { cx: 20, cy: 80 }, { cx: 65, cy: 30 }, { cx: 60, cy: 65 },
  { cx: 60, cy: 95 }, { cx: 65, cy: 130 }, { cx: 120, cy: 45 },
  { cx: 115, cy: 80 }, { cx: 120, cy: 115 }, { cx: 190, cy: 35 },
  { cx: 210, cy: 82, active: true }, { cx: 195, cy: 125 },
];

// Team B (emerald) dots for pitch radar
export const teamBCentroidsRadar = [
  { cx: 280, cy: 80 }, { cx: 235, cy: 35 }, { cx: 220, cy: 65 },
  { cx: 220, cy: 95 }, { cx: 235, cy: 125 }, { cx: 170, cy: 50 },
  { cx: 165, cy: 80 }, { cx: 170, cy: 110 }, { cx: 130, cy: 40 },
  { cx: 110, cy: 80 }, { cx: 130, cy: 120 },
];
