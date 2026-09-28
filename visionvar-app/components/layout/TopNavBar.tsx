'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { mockMatch, AVATAR_URL } from '@/lib/mockData/match';

const getNavLinks = (sessionId: string) => [
  { label: 'Live Workspace', path: `/sessions/${sessionId}` },
  { label: 'Offside Review', path: `/sessions/${sessionId}/offside-review` },
  { label: 'Formation & Radar', path: `/sessions/${sessionId}/formation` },
  { label: 'Event Timeline', path: `/sessions/${sessionId}/timeline` },
  { label: 'Player Analytics', path: `/sessions/${sessionId}/players` },
  { label: 'Match Summary', path: `/sessions/${sessionId}/summary` },
];

import { useParams } from 'next/navigation';

export default function TopNavBar() {
  const pathname = usePathname();
  const params = useParams();
  const sessionId = (params?.id as string) || mockMatch.id;
  const navLinks = getNavLinks(sessionId);

  return (
    <header
      className="sticky top-0 z-50 flex items-center justify-between w-full px-4 h-14"
      style={{
        background: 'rgba(24,28,34,0.85)',
        backdropFilter: 'blur(16px)',
        borderBottom: '1px solid rgba(59,75,61,0.3)',
        boxShadow: '0 1px 12px rgba(0,0,0,0.4)',
      }}
    >
      {/* Brand + Nav */}
      <div className="flex items-center gap-4 flex-1 min-w-0">
        {/* Logo */}
        <Link href="/sessions" className="flex items-center gap-2 shrink-0">
          <span
            className="inline-flex items-center justify-center w-7 h-7 rounded text-[#00e479]"
            style={{
              background: '#1c2026',
              border: '1px solid rgba(0,228,121,0.4)',
              boxShadow: '0 0 10px rgba(0,255,136,0.3)',
            }}
          >
            <span className="material-symbols-outlined text-[18px]">videocam</span>
          </span>
          <span className="text-headline-sm font-headline-sm font-bold tracking-tight text-[#00e479]">VisionVAR</span>
          <span
            className="text-label-sm font-label-sm text-[#00daf3] px-1.5 py-0.5 rounded ml-1"
            style={{ background: '#262a31', border: '1px solid rgba(59,75,61,0.5)' }}
          >
            CV v4.2
          </span>
        </Link>

        {/* Nav links */}
        <nav className="hidden md:flex items-center gap-3 lg:gap-4 pl-4 flex-1 overflow-x-auto no-scrollbar mask-edge" style={{ borderLeft: '1px solid rgba(59,75,61,0.4)' }}>
          {navLinks.map(({ label, path }) => {
            const isActive = pathname === path;
            return (
              <Link
                key={path}
                href={path}
                className="font-label-md text-label-md transition-all duration-150 hover:text-[#00e479] pb-1 whitespace-nowrap shrink-0"
                style={
                  isActive
                    ? { color: '#00e479', borderBottom: '2px solid #00e479' }
                    : { color: '#b9cbb9' }
                }
              >
                {label}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Trailing actions */}
      <div className="flex items-center gap-3 shrink-0">
        {/* Live status pill */}
        <div
          className="hidden xl:flex items-center gap-2 px-2.5 py-1 rounded text-label-sm font-label-sm text-[#b9cbb9]"
          style={{ background: '#1c2026', border: '1px solid rgba(59,75,61,0.5)' }}
        >
          <span className="w-2 h-2 rounded-full bg-[#00e479] animate-pulse-subtle" />
          <span>4K RAW · 12ms</span>
        </div>

        {/* Icon buttons */}
        <div className="flex items-center gap-1 text-[#b9cbb9]">
          {['videocam', 'settings', 'fullscreen'].map((icon) => (
            <button
              key={icon}
              className="w-8 h-8 flex items-center justify-center rounded transition-all duration-150 hover:text-[#00e479]"
              style={{ ':hover': { background: '#262a31' } } as React.CSSProperties}
              onMouseEnter={(e) => (e.currentTarget.style.background = '#262a31')}
              onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
            >
              <span className="material-symbols-outlined text-[18px]">{icon}</span>
            </button>
          ))}
        </div>

        {/* Export Telemetry */}
        <button
          className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 rounded text-label-md font-label-md text-[#00daf3] transition-all active:scale-95"
          style={{ background: '#1c2026', border: '1px solid rgba(59,75,61,0.6)' }}
        >
          <span className="material-symbols-outlined text-[15px]">download</span>
          Export Telemetry
        </button>

        {/* Broadcast Stream */}
        <button
          className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded text-label-md font-label-md font-semibold text-[#003919] transition-all active:scale-95 hover:brightness-110"
          style={{
            background: '#00ff88',
            boxShadow: '0 0 16px rgba(0,255,136,0.35)',
          }}
        >
          <span className="material-symbols-outlined text-[16px]">podcasts</span>
          Broadcast Stream
        </button>

        {/* Avatar */}
        <div
          className="w-8 h-8 rounded overflow-hidden ml-1 shrink-0"
          style={{ border: '1px solid rgba(0,228,121,0.4)' }}
        >
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={AVATAR_URL} alt="VAR Official" className="w-full h-full object-cover" />
        </div>
      </div>
    </header>
  );
}
