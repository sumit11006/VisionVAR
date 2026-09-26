'use client';

import { useState } from 'react';

interface CameraAngleSwitcherProps {
  cameras: { id: string; label: string }[];
  initialCamera?: string;
}

export default function CameraAngleSwitcher({ cameras, initialCamera }: CameraAngleSwitcherProps) {
  const [active, setActive] = useState(initialCamera ?? cameras[0]?.id);

  return (
    <div
      className="flex items-center gap-1.5 p-1 rounded"
      style={{ background: 'rgba(24,28,34,0.85)', backdropFilter: 'blur(12px)', border: '1px solid rgba(59,75,61,0.5)' }}
    >
      <span className="text-label-sm font-label-sm text-[#b9cbb9] px-2 uppercase tracking-wider font-bold">CAM:</span>
      {cameras.map(cam => (
        <button
          key={cam.id}
          onClick={() => setActive(cam.id)}
          className="px-2.5 py-1 rounded text-label-sm font-label-sm transition-all font-semibold"
          style={active === cam.id
            ? { background: '#00ff88', color: '#003919', boxShadow: '0 0 8px rgba(0,255,136,0.3)' }
            : { color: '#dfe2eb' }}
        >
          {cam.label}
        </button>
      ))}
    </div>
  );
}
