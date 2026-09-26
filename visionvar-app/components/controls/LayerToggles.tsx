'use client';

import { useState } from 'react';

interface Toggle {
  id: string;
  label: string;
  color: string;
  defaultOn?: boolean;
}

interface LayerTogglesProps {
  toggles?: Toggle[];
}

const DEFAULT_TOGGLES: Toggle[] = [
  { id: 'boxes',        label: 'Bounding Box',  color: '#00e479', defaultOn: true },
  { id: 'trajectories', label: 'Vector Arc',     color: '#00daf3', defaultOn: true },
  { id: 'offside',      label: 'Offside Plane',  color: '#849585', defaultOn: false },
];

export default function LayerToggles({ toggles = DEFAULT_TOGGLES }: LayerTogglesProps) {
  const [active, setActive] = useState<string[]>(
    toggles.filter(t => t.defaultOn).map(t => t.id)
  );

  const toggle = (id: string) => {
    setActive(prev => prev.includes(id) ? prev.filter(v => v !== id) : [...prev, id]);
  };

  return (
    <div
      className="flex items-center gap-1.5 p-1 rounded"
      style={{ background: 'rgba(24,28,34,0.85)', backdropFilter: 'blur(12px)', border: '1px solid rgba(59,75,61,0.5)' }}
    >
      {toggles.map(t => {
        const on = active.includes(t.id);
        return (
          <button
            key={t.id}
            onClick={() => toggle(t.id)}
            className="px-2.5 py-1 rounded text-label-sm font-label-sm flex items-center gap-1 transition-all"
            style={on
              ? { background: '#262a31', color: t.color, border: `1px solid ${t.color}60` }
              : { color: '#b9cbb9' }}
          >
            <span className="inline-block w-1.5 h-1.5 rounded-full" style={{ background: on ? t.color : '#849585' }} />
            {t.label}
          </button>
        );
      })}
      <button
        className="px-2 py-1 rounded text-label-sm font-label-sm text-[#dfe2eb] transition-all"
        style={{ background: 'rgba(38,42,49,0.6)' }}
      >
        <span className="material-symbols-outlined text-[14px]">tune</span>
      </button>
    </div>
  );
}
