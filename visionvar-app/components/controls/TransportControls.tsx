'use client';

import { useState } from 'react';

interface TransportControlsProps {
  scrubberSeconds: number;
  onStep?: (delta: number) => void;
}

const SPEEDS = ['0.25x', '0.5x', '1.0x', '2.0x'];

export default function TransportControls({ scrubberSeconds, onStep }: TransportControlsProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [speed, setSpeed] = useState('1.0x');

  const minutes = Math.floor(scrubberSeconds / 60);
  const secs    = scrubberSeconds % 60;
  const phase   = scrubberSeconds > 2700 ? 'In Possession • Attacking Final Third' : 'Defensive Shape • Mid-block';

  return (
    <div className="flex items-center justify-between pt-1">
      {/* Left: phase tag */}
      <div className="flex items-center gap-2">
        <span className="text-label-sm font-label-sm uppercase tracking-wider text-[#849585]">Phase:</span>
        <span
          className="px-2 py-0.5 rounded text-label-sm font-label-sm text-[#00e479]"
          style={{ background: '#262a31', border: '1px solid rgba(0,228,121,0.3)' }}
        >
          {phase}
        </span>
        <span className="hidden sm:inline text-label-sm font-label-sm text-[#b9cbb9]">
          Rec: <span style={{ color: '#00daf3' }}>SYNCHRONIZED</span>
        </span>
      </div>

      {/* Center: playback */}
      <div className="flex items-center gap-2">
        <button
          onClick={() => onStep?.(-30)}
          className="p-1.5 rounded transition-all active:scale-95"
          style={{ background: '#1c2026' }}
          title="Step back (-1F)"
        >
          <span className="material-symbols-outlined text-[18px] text-[#dfe2eb]">skip_previous</span>
        </button>

        <button
          onClick={() => setIsPlaying(v => !v)}
          className="w-9 h-9 rounded-full flex items-center justify-center font-bold transition-all active:scale-95 hover:brightness-110"
          style={{ background: '#00ff88', boxShadow: '0 0 12px rgba(0,255,136,0.4)' }}
        >
          <span className="material-symbols-outlined text-[22px] text-[#003919]" style={{ fontVariationSettings: "'FILL' 1" }}>
            {isPlaying ? 'pause' : 'play_arrow'}
          </span>
        </button>

        <button
          onClick={() => onStep?.(30)}
          className="p-1.5 rounded transition-all active:scale-95"
          style={{ background: '#1c2026' }}
          title="Step forward (+1F)"
        >
          <span className="material-symbols-outlined text-[18px] text-[#dfe2eb]">skip_next</span>
        </button>

        <div className="h-4 w-px mx-2" style={{ background: 'rgba(59,75,61,0.4)' }} />

        {/* Speed selector */}
        <div
          className="flex items-center rounded p-0.5 text-label-sm font-label-sm"
          style={{ background: '#1c2026', border: '1px solid rgba(59,75,61,0.3)' }}
        >
          {SPEEDS.map(s => (
            <button
              key={s}
              onClick={() => setSpeed(s)}
              className="px-2 py-0.5 rounded transition-all"
              style={s === speed
                ? { background: '#262a31', color: '#00e479', fontWeight: 700 }
                : { color: '#b9cbb9' }}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Right: zoom & volume */}
      <div className="flex items-center gap-3">
        <div className="hidden md:flex items-center gap-1.5 text-label-sm font-label-sm text-[#b9cbb9]">
          <span>ZOOM:</span>
          {['1.0x', '2.0x', '4.0x'].map((z, i) => (
            <button
              key={z}
              className="px-1.5 py-0.5 rounded font-mono transition-all"
              style={i === 0
                ? { background: '#1c2026', color: '#00e479' }
                : { background: '#1c2026', color: '#dfe2eb' }}
            >
              {z}
            </button>
          ))}
        </div>
        <button className="p-1 rounded transition-all text-[#b9cbb9]">
          <span className="material-symbols-outlined text-[18px]">volume_up</span>
        </button>
      </div>
    </div>
  );
}
