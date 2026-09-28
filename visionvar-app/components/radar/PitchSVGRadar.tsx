interface PitchSVGRadarProps {
  teamADots?: { cx: number; cy: number; active?: boolean; trail?: {cx: number, cy: number}[] }[];
  teamBDots?: { cx: number; cy: number; trail?: {cx: number, cy: number}[] }[];
  ballPos?: { cx: number; cy: number; trail?: {cx: number, cy: number}[] };
  defensiveLine?: number;
  height?: string;
}

const DEFAULT_TEAM_A = [
  { cx: 20, cy: 80 }, { cx: 65, cy: 30 }, { cx: 60, cy: 65 },
  { cx: 60, cy: 95 }, { cx: 65, cy: 130 }, { cx: 120, cy: 45 },
  { cx: 115, cy: 80 }, { cx: 120, cy: 115 }, { cx: 190, cy: 35 },
  { cx: 210, cy: 82, active: true }, { cx: 195, cy: 125 },
];
const DEFAULT_TEAM_B = [
  { cx: 280, cy: 80 }, { cx: 235, cy: 35 }, { cx: 220, cy: 65 },
  { cx: 220, cy: 95 }, { cx: 235, cy: 125 }, { cx: 170, cy: 50 },
  { cx: 165, cy: 80 }, { cx: 170, cy: 110 }, { cx: 130, cy: 40 },
  { cx: 110, cy: 80 }, { cx: 130, cy: 120 },
];

export default function PitchSVGRadar({
  teamADots = DEFAULT_TEAM_A,
  teamBDots = DEFAULT_TEAM_B,
  ballPos,
  defensiveLine = 195,
  height = 'h-36',
}: PitchSVGRadarProps) {
  return (
    <div
      className={`relative w-full ${height} rounded overflow-hidden flex items-center justify-center`}
      style={{ background: '#0a0e14', border: '1px solid rgba(59,75,61,0.4)' }}
    >
      <svg className="w-full h-full p-2" viewBox="0 0 300 160">
        {/* Boundary */}
        <rect x="2" y="2" width="296" height="156" fill="none" stroke="#3b4b3d" strokeWidth="1.2" />
        {/* Halfway */}
        <line x1="150" y1="2" x2="150" y2="158" stroke="#3b4b3d" strokeWidth="1.2" />
        {/* Center circle */}
        <circle cx="150" cy="80" r="28" fill="none" stroke="#3b4b3d" strokeWidth="1.2" />
        <circle cx="150" cy="80" r="2" fill="#3b4b3d" />
        {/* Left penalty area */}
        <rect x="2" y="32" width="48" height="96" fill="none" stroke="#3b4b3d" strokeWidth="1.2" />
        {/* Right penalty area */}
        <rect x="250" y="32" width="48" height="96" fill="none" stroke="#3b4b3d" strokeWidth="1.2" />
        {/* Defensive line */}
        <line x1={defensiveLine} y1="4" x2={defensiveLine} y2="156" stroke="#ffb4ab" strokeDasharray="3 3" strokeWidth="1.5" />
        {/* Team A (cyan) */}
        {teamADots.map((d, i) => (
          <g key={i}>
            {d.trail && d.trail.length > 1 && (
              <polyline 
                points={d.trail.map(t => `${t.cx},${t.cy}`).join(' ')} 
                fill="none" 
                stroke="rgba(0, 218, 243, 0.4)" 
                strokeWidth="1.5" 
                strokeDasharray="2,2" 
              />
            )}
            {d.active ? (
              <circle cx={d.cx} cy={d.cy} r="4.5" fill="#00daf3" stroke="#ffffff" strokeWidth="1.2" className="animate-pulse" />
            ) : (
              <circle cx={d.cx} cy={d.cy} r="3.5" fill="#00daf3" />
            )}
          </g>
        ))}
        {/* Team B (emerald) */}
        {teamBDots.map((d, i) => (
          <g key={i}>
            {d.trail && d.trail.length > 1 && (
              <polyline 
                points={d.trail.map(t => `${t.cx},${t.cy}`).join(' ')} 
                fill="none" 
                stroke="rgba(0, 228, 121, 0.4)" 
                strokeWidth="1.5" 
                strokeDasharray="2,2" 
              />
            )}
            <circle cx={d.cx} cy={d.cy} r="3.5" fill="#00e479" />
          </g>
        ))}
        {/* Ball */}
        {ballPos && (
          <g>
            {ballPos.trail && ballPos.trail.length > 1 && (
              <polyline 
                points={ballPos.trail.map(t => `${t.cx},${t.cy}`).join(' ')} 
                fill="none" 
                stroke="rgba(255, 255, 255, 0.6)" 
                strokeWidth="2.0" 
                strokeDasharray="3,3" 
              />
            )}
            <circle cx={ballPos.cx} cy={ballPos.cy} r="3" fill="#ffffff" className="glow-cyan" />
          </g>
        )}
      </svg>
    </div>
  );
}
