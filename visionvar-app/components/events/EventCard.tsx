import type { MatchEvent } from '@/types';

const typeConfig: Record<string, { bg: string; border: string; text: string; icon: string; label: string }> = {
  GOAL:             { bg: 'rgba(250,204,21,0.2)', border: 'rgba(250,204,21,0.5)', text: '#facc15', icon: 'sports_soccer', label: 'GOAL' },
  GOAL_UNDER_REVIEW:{ bg: 'rgba(0,255,136,0.15)', border: 'rgba(0,228,121,0.6)', text: '#00e479', icon: 'sports_soccer', label: 'GOAL / POSSIBLE OFFSIDE' },
  YELLOW_CARD:      { bg: 'rgba(245,158,11,0.15)', border: 'rgba(245,158,11,0.4)', text: '#f59e0b', icon: 'style', label: 'YELLOW CARD' },
  RED_CARD:         { bg: 'rgba(147,0,10,0.3)', border: 'rgba(255,180,171,0.4)', text: '#ffdad6', icon: 'style', label: 'RED CARD' },
  OFFSIDE:          { bg: 'rgba(0,218,243,0.1)', border: 'rgba(0,218,243,0.4)', text: '#00daf3', icon: 'flag', label: 'OFFSIDE FLAG' },
  PENALTY_RESCINDED:{ bg: 'rgba(192,193,255,0.1)', border: 'rgba(192,193,255,0.3)', text: '#c0c1ff', icon: 'gavel', label: 'PENALTY RESCINDED' },
  HIGH_DANGER_FOUL: { bg: 'rgba(147,0,10,0.25)', border: 'rgba(255,180,171,0.35)', text: '#ffb4ab', icon: 'warning', label: 'HIGH-DANGER FOUL' },
  SUBSTITUTION:     { bg: 'rgba(59,75,61,0.3)', border: 'rgba(59,75,61,0.5)', text: '#b9cbb9', icon: 'swap_horiz', label: 'SUBSTITUTION' },
  VAR_INTERVENTION: { bg: 'rgba(0,228,121,0.1)', border: 'rgba(0,228,121,0.4)', text: '#00e479', icon: 'live_tv', label: 'VAR INTERVENTION' },
};

const verdictStyle = (verdict: string | null) => {
  if (!verdict) return null;
  if (verdict.includes('REVIEW')) return { color: '#00daf3', border: '1px solid rgba(0,218,243,0.5)', bg: 'rgba(0,218,243,0.1)' };
  if (verdict.includes('VALIDATED')) return { color: '#00e479', border: '1px solid rgba(0,228,121,0.5)', bg: 'rgba(0,228,121,0.1)' };
  return { color: '#b9cbb9', border: '1px solid rgba(59,75,61,0.4)', bg: '#262a31' };
};

interface EventCardProps {
  event: MatchEvent;
  isActive?: boolean;
}

export default function EventCard({ event, isActive }: EventCardProps) {
  const cfg = typeConfig[event.type] ?? typeConfig.VAR_INTERVENTION;
  const vStyle = verdictStyle(event.aiVerdict);

  return (
    <div
      className="rounded-lg p-3 relative transition-all cursor-pointer"
      style={isActive
        ? { background: 'rgba(28,32,38,0.9)', border: '2px solid #00e479', boxShadow: '0 0 16px rgba(0,228,121,0.25)' }
        : { background: 'rgba(28,32,38,0.6)', border: '1px solid rgba(59,75,61,0.3)' }}
    >
      {/* Header row */}
      <div className="flex items-start justify-between gap-2 mb-2">
        <div className="flex items-center gap-2 flex-wrap">
          <span
            className="px-2 py-0.5 rounded text-label-md font-label-md font-mono"
            style={{ background: '#0a0e14', color: isActive ? '#00e479' : '#b9cbb9', border: `1px solid ${isActive ? 'rgba(0,228,121,0.4)' : 'rgba(59,75,61,0.2)'}` }}
          >
            {event.minute.toString().padStart(2,'0')}:{event.second.toString().padStart(2,'0')} — Frame #{event.frameId.toLocaleString()}
          </span>
          <span
            className="px-2 py-0.5 rounded text-label-sm font-label-sm font-bold flex items-center gap-1"
            style={{ background: cfg.bg, border: `1px solid ${cfg.border}`, color: cfg.text }}
          >
            <span className="material-symbols-outlined text-[11px]">{cfg.icon}</span>
            {cfg.label}
          </span>
        </div>
        {/* AI Verdict */}
        {vStyle && (
          <span
            className="px-2 py-0.5 rounded text-label-sm font-label-sm font-bold tracking-wider flex items-center gap-1 shrink-0 whitespace-nowrap"
            style={{ background: vStyle.bg, border: vStyle.border, color: vStyle.color }}
          >
            {event.aiVerdict}
          </span>
        )}
      </div>

      {/* Player row */}
      {event.player && (
        <div className="flex items-center justify-between gap-2 border-b pb-2 mb-2" style={{ borderColor: 'rgba(59,75,61,0.3)' }}>
          <div className="flex items-center gap-3">
            <div
              className="w-8 h-8 rounded-full flex items-center justify-center font-bold text-[#dfe2eb] text-headline-sm font-headline-sm"
              style={{ background: '#262a31', border: '1px solid rgba(59,75,61,0.5)' }}
            >
              {event.playerJersey ?? '—'}
            </div>
            <div>
              <div className="text-body-md font-body-md font-bold text-[#f1ffef] flex items-center gap-2">
                {event.player}
                {event.playerTeam && <span className="text-label-sm font-label-sm text-[#849585] font-normal">{event.playerTeam}</span>}
              </div>
              {event.description && <div className="text-body-sm font-body-sm text-[#b9cbb9] mt-0.5 line-clamp-2">{event.description}</div>}
            </div>
          </div>
          <button
            className="px-3 py-1.5 rounded text-label-sm font-label-sm flex items-center gap-1.5 shrink-0 transition-all active:scale-95"
            style={{ background: '#31353c', color: '#00e479', border: '1px solid rgba(59,75,61,0.5)' }}
          >
            <span className="material-symbols-outlined text-[11px]">replay</span>
            Jump to Broadcast
          </button>
        </div>
      )}

      {/* Micro-stat bento */}
      {(event.xg !== null && event.xg !== undefined) && (
        <div className="grid grid-cols-4 gap-2 font-mono text-label-sm mb-2">
          {event.ballVelocityKph && (
            <div className="p-1.5 rounded" style={{ background: 'rgba(10,14,20,0.8)', border: '1px solid rgba(59,75,61,0.2)' }}>
              <span className="text-[#849585] block text-[9px]">BALL VEL</span>
              <span className="text-[#dfe2eb] font-bold text-xs">{event.ballVelocityKph} km/h</span>
            </div>
          )}
          {event.xg !== undefined && event.xg !== null && (
            <div className="p-1.5 rounded" style={{ background: 'rgba(10,14,20,0.8)', border: '1px solid rgba(59,75,61,0.2)' }}>
              <span className="text-[#849585] block text-[9px]">SHOT xG</span>
              <span className="text-[#00e479] font-bold text-xs">{event.xg} xG</span>
            </div>
          )}
          {event.impactGForce && (
            <div className="p-1.5 rounded" style={{ background: 'rgba(10,14,20,0.8)', border: '1px solid rgba(59,75,61,0.2)' }}>
              <span className="text-[#849585] block text-[9px]">IMPACT</span>
              <span className="text-[#dfe2eb] font-bold text-xs">{event.impactGForce} G</span>
            </div>
          )}
          {event.saotMarginCm !== undefined && (
            <div className="p-1.5 rounded" style={{ background: 'rgba(10,14,20,0.8)', border: '1px solid rgba(59,75,61,0.2)' }}>
              <span className="text-[#849585] block text-[9px]">SAOT MARGIN</span>
              <span className="text-[#00daf3] font-bold text-xs">+{event.saotMarginCm} cm</span>
            </div>
          )}
        </div>
      )}

      {/* AI explanation */}
      {event.aiExplanation && (
        <div
          className="mt-1 rounded p-2 text-body-sm font-mono flex items-start gap-2"
          style={{ background: 'rgba(10,14,20,0.9)', border: '1px solid rgba(59,75,61,0.4)' }}
        >
          <span className="material-symbols-outlined text-[#00daf3] text-sm mt-0.5">analytics</span>
          <div className="text-[#b9cbb9] leading-relaxed">
            <strong style={{ color: '#00e479' }}>AI Explanation: </strong>
            {event.aiExplanation}
          </div>
        </div>
      )}
    </div>
  );
}
