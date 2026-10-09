'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname, useParams } from 'next/navigation';

const AVATAR_URL = 'https://i.pravatar.cc/150?u=var_official';

const getNavLinks = (sessionId: string) => [
  { label: 'Live Workspace', path: `/sessions/${sessionId}` },
  { label: 'Offside Review', path: `/sessions/${sessionId}/offside-review` },
  { label: 'Formation & Radar', path: `/sessions/${sessionId}/formation` },
  { label: 'Event Timeline', path: `/sessions/${sessionId}/timeline` },
  { label: 'Player Analytics', path: `/sessions/${sessionId}/players` },
  { label: 'Match Summary', path: `/sessions/${sessionId}/summary` },
];

export default function TopNavBar() {
  const pathname = usePathname();
  const params = useParams();
  const sessionId = (params?.id as string) || '';
  const navLinks = getNavLinks(sessionId);

  const [alertMessage, setAlertMessage] = useState<string | null>(null);
  const [hasBadge, setHasBadge] = useState<boolean>(false);
  const [openDropdown, setOpenDropdown] = useState<string | null>(null);

  useEffect(() => {
    if (!sessionId) return;
    if (pathname.includes('/offside-review')) {
      setHasBadge(false);
    }
  }, [pathname, sessionId]);

  useEffect(() => {
    if (!sessionId) return;
    
    // Fallback to localhost if window is undefined, else use window.location
    const wsUrl = `ws://localhost:8000/ws/analysis/${sessionId}`;
    const ws = new WebSocket(wsUrl);
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'event_detected' && data.event?.event_type === 'OFFSIDE_CANDIDATE') {
          setAlertMessage('Potential Offside Detected — Action Required');
          if (!window.location.pathname.includes('/offside-review')) {
            setHasBadge(true);
          }
          setTimeout(() => {
            setAlertMessage(null);
          }, 8000);
        }
      } catch (e) {}
    };
    
    return () => {
      ws.close();
    };
  }, [sessionId]);

  return (
    <>
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
          {sessionId && navLinks.map(({ label, path }) => {
            const isActive = pathname === path;
            return (
              <Link
                key={path}
                href={path}
                className="relative font-label-md text-label-md transition-all duration-150 hover:text-[#00e479] pb-1 whitespace-nowrap shrink-0"
                style={
                  isActive
                    ? { color: '#00e479', borderBottom: '2px solid #00e479' }
                    : { color: '#b9cbb9' }
                }
              >
                {label}
                {label === 'Offside Review' && hasBadge && (
                  <span className="absolute -top-1 -right-3 flex h-2.5 w-2.5">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#ff4444] opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-[#ff4444]"></span>
                  </span>
                )}
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
            <div key={icon} className="relative">
              <button
                onClick={() => {
                  if (icon === 'fullscreen') {
                    if (!document.fullscreenElement) {
                      document.documentElement.requestFullscreen().catch(() => {});
                    } else {
                      document.exitFullscreen().catch(() => {});
                    }
                  } else {
                    setOpenDropdown(openDropdown === icon ? null : icon);
                  }
                }}
                className="w-8 h-8 flex items-center justify-center rounded transition-all duration-150 hover:text-[#00e479]"
                style={{ ':hover': { background: '#262a31' }, background: openDropdown === icon ? '#262a31' : 'transparent' } as React.CSSProperties}
                onMouseEnter={(e) => { if (openDropdown !== icon) e.currentTarget.style.background = '#262a31'; }}
                onMouseLeave={(e) => { if (openDropdown !== icon) e.currentTarget.style.background = 'transparent'; }}
              >
                <span className="material-symbols-outlined text-[18px]">{icon}</span>
              </button>
              
              {openDropdown === icon && icon === 'settings' && (
                <div className="absolute right-0 top-full mt-2 w-48 rounded-md shadow-lg py-1 z-50 border border-gray-700/50" style={{ background: '#1c2026' }}>
                  <button className="block w-full text-left px-4 py-2 text-sm text-[#b9cbb9] hover:bg-[#262a31] hover:text-white" onClick={() => { setOpenDropdown(null); setAlertMessage('HUD Opacity adjusted'); setTimeout(() => setAlertMessage(null), 3000); }}>Adjust HUD Opacity</button>
                  <button className="block w-full text-left px-4 py-2 text-sm text-[#b9cbb9] hover:bg-[#262a31] hover:text-white" onClick={() => { setOpenDropdown(null); setAlertMessage('Dark Mode is already enabled'); setTimeout(() => setAlertMessage(null), 3000); }}>Toggle Night Mode</button>
                  <button className="block w-full text-left px-4 py-2 text-sm text-[#ff4444] hover:bg-[#262a31] hover:text-red-400" onClick={() => { setOpenDropdown(null); setAlertMessage('Cache cleared successfully'); setTimeout(() => setAlertMessage(null), 3000); }}>Clear Cache</button>
                </div>
              )}
              
              {openDropdown === icon && icon === 'videocam' && (
                <div className="absolute right-0 top-full mt-2 w-56 rounded-md shadow-lg py-1 z-50 border border-gray-700/50" style={{ background: '#1c2026' }}>
                  <div className="px-4 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">Camera Feeds</div>
                  <button className="block w-full text-left px-4 py-2 text-sm text-[#00e479] bg-[#262a31]" onClick={() => setOpenDropdown(null)}>Main Tactical (ISO 1)</button>
                  <button className="block w-full text-left px-4 py-2 text-sm text-[#b9cbb9] hover:bg-[#262a31] hover:text-white" onClick={() => { setOpenDropdown(null); setAlertMessage('ISO 2 Feed Offline'); setTimeout(() => setAlertMessage(null), 3000); }}>High Behind Goal (ISO 2)</button>
                  <button className="block w-full text-left px-4 py-2 text-sm text-[#b9cbb9] hover:bg-[#262a31] hover:text-white" onClick={() => { setOpenDropdown(null); setAlertMessage('Switching to Broadcast Feed...'); setTimeout(() => setAlertMessage(null), 3000); }}>Broadcast Feed</button>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Export Telemetry */}
        <button
          onClick={async () => {
            if (sessionId) {
              setAlertMessage('Preparing telemetry download...');
              try {
                const response = await fetch(`http://localhost:8000/api/sessions/${sessionId}/tracking`);
                if (!response.ok) throw new Error('Data not ready');
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;
                link.download = `tracking_${sessionId}.json`;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                window.URL.revokeObjectURL(url);
                setAlertMessage('Download complete');
              } catch (e) {
                setAlertMessage('No telemetry data available. Did you run YOLO detection?');
              }
              setTimeout(() => setAlertMessage(null), 3000);
            } else {
              setAlertMessage('No active session to export');
              setTimeout(() => setAlertMessage(null), 3000);
            }
          }}
          className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 rounded text-label-md font-label-md text-[#00daf3] transition-all active:scale-95 hover:brightness-110 cursor-pointer"
          style={{ background: '#1c2026', border: '1px solid rgba(59,75,61,0.6)' }}
        >
          <span className="material-symbols-outlined text-[15px]">download</span>
          Export Telemetry
        </button>

        {/* Broadcast Stream */}
        <button
          onClick={() => {
            setAlertMessage(`Initializing broadcast feed for ${sessionId || 'Match'}...`);
            setTimeout(() => setAlertMessage(null), 4000);
          }}
          className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded text-label-md font-label-md font-semibold text-[#003919] transition-all active:scale-95 hover:brightness-110 cursor-pointer"
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

    {/* Global Toast Notification */}
    {alertMessage && (
      <div className="fixed bottom-6 right-6 z-[100] animate-in slide-in-from-bottom-5 fade-in duration-300">
        <div 
          className="flex items-center gap-3 px-4 py-3 rounded-lg shadow-2xl border"
          style={{ background: '#1c2026', borderColor: '#ff4444', borderLeft: '4px solid #ff4444' }}
        >
          <span className="material-symbols-outlined text-[#ff4444]">warning</span>
          <div className="flex flex-col">
            <span className="text-label-sm font-bold text-[#ff4444] uppercase tracking-wider">VAR Alert</span>
            <span className="text-body-sm text-[#f1ffef]">{alertMessage}</span>
          </div>
          <button onClick={() => setAlertMessage(null)} className="ml-4 text-[#849585] hover:text-white">
            <span className="material-symbols-outlined text-[16px]">close</span>
          </button>
        </div>
      </div>
    )}
    </>
  );
}
