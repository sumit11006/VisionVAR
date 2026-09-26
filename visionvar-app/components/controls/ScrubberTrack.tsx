'use client';

import { useState, useEffect } from 'react';

export interface TimelineEventStamp {
  timeSeconds: number;
  label: string;
  color: string;
}

interface ScrubberTrackProps {
  onValueChange?: (currentSeconds: number, currentFrame?: number) => void;
  currentSeconds?: number;
  durationSeconds?: number;
  fps?: number;
  totalFrames?: number;
  events?: TimelineEventStamp[];
  initialValue?: number;
  maxValue?: number;
}

function formatTickLabel(seconds: number, totalDuration: number): string {
  if (totalDuration <= 60) {
    // Under 1 minute: format as seconds e.g. "0s", "3s", "6s", "9s", "12s"
    if (Number.isInteger(seconds) || Math.abs(seconds - Math.round(seconds)) < 0.05) {
      return `${Math.round(seconds)}s`;
    }
    return `${seconds.toFixed(1)}s`;
  }
  // Over 1 minute: format as M:SS
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

export default function ScrubberTrack({
  onValueChange,
  currentSeconds,
  durationSeconds,
  fps = 30.0,
  totalFrames,
  events = [],
  initialValue,
  maxValue,
}: ScrubberTrackProps) {
  // Resolve actual duration in seconds
  const resolvedDuration = durationSeconds ?? (maxValue && maxValue !== 5400 ? maxValue : 12.0);
  const effectiveFps = fps > 0 ? fps : 30.0;

  // Local state if uncontrolled
  const [internalSeconds, setInternalSeconds] = useState<number>(() => {
    if (currentSeconds !== undefined) return currentSeconds;
    if (initialValue !== undefined && initialValue <= (durationSeconds || 120)) return initialValue;
    return 0;
  });

  // Sync when controlled prop changes
  useEffect(() => {
    if (currentSeconds !== undefined) {
      setInternalSeconds(currentSeconds);
    }
  }, [currentSeconds]);

  const activeSeconds = currentSeconds !== undefined ? currentSeconds : internalSeconds;
  const playheadPct = resolvedDuration > 0
    ? Math.min(100, Math.max(0, (activeSeconds / resolvedDuration) * 100))
    : 0;

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const s = parseFloat(e.target.value);
    setInternalSeconds(s);
    const frame = Math.round(s * effectiveFps);
    onValueChange?.(s, frame);
  };

  // Generate 5 dynamic ticks: 0, 25%, 50%, 75%, 100%
  const tickValues = [
    0,
    resolvedDuration * 0.25,
    resolvedDuration * 0.5,
    resolvedDuration * 0.75,
    resolvedDuration,
  ];

  // Filter events strictly to those occurring within video duration
  const validEvents = events.filter((e) => e.timeSeconds >= 0 && e.timeSeconds <= resolvedDuration);

  return (
    <div className="relative w-full flex flex-col gap-1">
      {/* Event indicators bar */}
      <div
        className="relative w-full h-5 rounded overflow-hidden"
        style={{ background: '#0a0e14', border: '1px solid rgba(59,75,61,0.3)' }}
      >
        {validEvents.map((evt, i) => {
          const pos = (evt.timeSeconds / resolvedDuration) * 100;
          return (
            <div
              key={i}
              className="absolute top-0 bottom-0 w-2.5 opacity-80 hover:opacity-100 cursor-pointer group"
              style={{ left: `${pos}%`, background: evt.color }}
              title={evt.label}
            />
          );
        })}

        {/* Playhead needle */}
        <div
          className="absolute top-0 bottom-0 w-[2px] pointer-events-none z-10 transition-all duration-75"
          style={{ left: `${playheadPct}%`, background: '#00ff88', boxShadow: '0 0 6px rgba(0,255,136,0.6)' }}
        >
          <span className="absolute -top-1 -left-[5px] w-3 h-3 rotate-45 rounded-sm" style={{ background: '#00ff88' }} />
        </div>

        {/* Dynamic ticks scaled to actual duration */}
        <div
          className="absolute inset-0 flex justify-between items-center px-2 pointer-events-none text-label-sm font-label-sm select-none"
          style={{ color: 'rgba(132,149,133,0.6)' }}
        >
          {tickValues.map((sec, idx) => {
            const isLast = idx === tickValues.length - 1;
            return (
              <span
                key={idx}
                style={isLast ? { color: '#00e479', fontWeight: 700 } : undefined}
              >
                {formatTickLabel(sec, resolvedDuration)}
              </span>
            );
          })}
        </div>
      </div>

      {/* Range slider */}
      <input
        type="range"
        min="0"
        max={resolvedDuration}
        step={1 / effectiveFps}
        value={activeSeconds}
        onChange={handleChange}
        className="timeline-scrub-bar w-full cursor-ew-resize"
      />
    </div>
  );
}

