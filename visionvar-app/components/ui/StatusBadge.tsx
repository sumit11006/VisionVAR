interface StatusBadgeProps {
  label: string;
  color?: 'emerald' | 'cyan' | 'crimson' | 'amber' | 'outline' | 'violet';
  ping?: boolean;
  pulse?: boolean;
  className?: string;
}

const colorMap = {
  emerald: { bg: 'rgba(0,228,121,0.15)', border: 'rgba(0,228,121,0.5)', text: '#00e479' },
  cyan:    { bg: 'rgba(0,218,243,0.15)', border: 'rgba(0,218,243,0.5)', text: '#00daf3' },
  crimson: { bg: 'rgba(147,0,10,0.4)',   border: 'rgba(255,180,171,0.4)', text: '#ffdad6' },
  amber:   { bg: 'rgba(245,158,11,0.15)', border: 'rgba(245,158,11,0.4)', text: '#facc15' },
  outline: { bg: '#262a31',              border: 'rgba(59,75,61,0.5)',   text: '#b9cbb9' },
  violet:  { bg: 'rgba(192,193,255,0.1)', border: 'rgba(192,193,255,0.3)', text: '#c0c1ff' },
};

export default function StatusBadge({ label, color = 'outline', ping, pulse, className = '' }: StatusBadgeProps) {
  const c = colorMap[color];
  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-label-sm font-label-sm font-bold tracking-wide uppercase ${pulse ? 'animate-pulse' : ''} ${className}`}
      style={{ background: c.bg, border: `1px solid ${c.border}`, color: c.text }}
    >
      {ping && <span className="w-1.5 h-1.5 rounded-full inline-block" style={{ background: c.text }} />}
      {label}
    </span>
  );
}
