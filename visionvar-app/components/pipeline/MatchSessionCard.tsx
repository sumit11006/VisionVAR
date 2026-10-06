import type { MatchSession } from '@/types';
import Link from 'next/link';

const statusConfig = {
  READY:      { label: 'READY',      color: '#00e479',  bg: 'rgba(0,228,121,0.1)',  border: 'rgba(0,228,121,0.4)' },
  ARCHIVED:   { label: 'ARCHIVED',   color: '#b9cbb9',  bg: 'rgba(59,75,61,0.3)',   border: 'rgba(59,75,61,0.5)' },
  PROCESSING: { label: 'PROCESSING', color: '#00daf3',  bg: 'rgba(0,218,243,0.1)',  border: 'rgba(0,218,243,0.4)' },
};

export default function MatchSessionCard({ session }: { session: MatchSession }) {
  const defaultCfg = { label: session.status?.toUpperCase() || 'UNKNOWN', color: '#888', bg: 'rgba(136,136,136,0.1)', border: 'rgba(136,136,136,0.4)' };
  const cfg = (statusConfig as any)[session.status?.toUpperCase()] || defaultCfg;

  return (
    <div
      className="rounded-xl overflow-hidden flex flex-col transition-all duration-200 hover:brightness-105"
      style={{ background: '#181c22', border: '1px solid rgba(59,75,61,0.4)' }}
    >
      {/* Thumbnail */}
      <div className="relative h-40 overflow-hidden">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src={session.imageUrl} alt={`${session.homeTeam} vs ${session.awayTeam}`} className="w-full h-full object-cover" />
        <div className="absolute inset-0" style={{ background: 'linear-gradient(to top, rgba(10,14,20,0.9), transparent 60%)' }} />
        {/* Status badge */}
        <span
          className="absolute top-2 right-2 px-2 py-0.5 rounded text-label-sm font-label-sm font-bold"
          style={{ background: cfg.bg, border: `1px solid ${cfg.border}`, color: cfg.color }}
        >
          {cfg.label}
        </span>
        {/* VAR alert badge */}
        {session.varAlerts && (
          <span
            className="absolute top-2 left-2 px-2 py-0.5 rounded text-label-sm font-label-sm font-bold flex items-center gap-1"
            style={{ background: 'rgba(147,0,10,0.6)', border: '1px solid rgba(255,180,171,0.4)', color: '#ffdad6' }}
          >
            <span className="material-symbols-outlined text-[12px]">flag</span>
            {session.varAlerts} VAR
          </span>
        )}
        {/* Processing bar */}
        {session.status === 'PROCESSING' && session.processingPercent !== undefined && (
          <div className="absolute bottom-0 left-0 right-0 h-1" style={{ background: '#262a31' }}>
            <div className="h-full" style={{ width: `${session.processingPercent}%`, background: '#00daf3' }} />
          </div>
        )}
      </div>

      {/* Body */}
      <div className="p-4 flex flex-col gap-3 flex-1">
        <div>
          <h3 className="text-headline-sm font-headline-sm text-[#f1ffef]">{session.homeTeam} vs {session.awayTeam}</h3>
          <p className="text-body-sm font-body-sm text-[#b9cbb9] mt-0.5">{session.competition} · {session.venue}</p>
        </div>

        {/* Stats micro-grid */}
        {session.status === 'READY' && (
          <div className="grid grid-cols-3 gap-2 text-label-sm font-label-sm">
            <div className="text-center">
              <div className="text-[#849585] uppercase text-[9px]">VAR Alerts</div>
              <div className="text-[#00e479] font-bold">{session.varAlerts}</div>
            </div>
            <div className="text-center">
              <div className="text-[#849585] uppercase text-[9px]">Offside Ck</div>
              <div className="text-[#dfe2eb] font-bold">{session.offsideChecks}</div>
            </div>
            <div className="text-center">
              <div className="text-[#849585] uppercase text-[9px]">Penalty Radar</div>
              <div className="text-[#dfe2eb] font-bold">{session.penaltyRadar}</div>
            </div>
          </div>
        )}

        {session.status === 'ARCHIVED' && (
          <div className="text-label-sm font-label-sm text-[#b9cbb9]">
            Archived {session.archivedHoursAgo}h ago
          </div>
        )}

        {session.status === 'PROCESSING' && (
          <div className="text-label-sm font-label-sm text-[#00daf3]">
            Processing {session.processingPercent}% · ETA {session.etaMinutes}m
          </div>
        )}

        {/* CTA */}
        <Link
          href={`/sessions/${session.id}`}
          className={`mt-auto block text-center py-2 rounded text-label-md font-label-md font-bold transition-all hover:brightness-110 active:scale-95 ${
            session.status === 'PROCESSING' ? 'animate-pulse' : ''
          }`}
          style={
            session.status === 'READY'
              ? { background: '#00ff88', color: '#003919', boxShadow: '0 0 12px rgba(0,255,136,0.35)' }
              : session.status === 'PROCESSING'
              ? { background: 'rgba(0,218,243,0.15)', color: '#00daf3', border: '1px solid rgba(0,218,243,0.5)' }
              : { background: '#262a31', color: '#b9cbb9', border: '1px solid rgba(59,75,61,0.4)' }
          }
        >
          {session.status === 'PROCESSING' ? 'View Live Feed →' : session.status === 'READY' ? 'Launch Workspace →' : 'View Archive →'}
        </Link>
      </div>
    </div>
  );
}
