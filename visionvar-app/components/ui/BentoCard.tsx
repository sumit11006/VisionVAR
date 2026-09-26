interface BentoCardProps {
  icon?: string;
  iconColor?: string;
  title: string;
  badge?: string;
  badgeColor?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  glowColor?: 'emerald' | 'cyan' | 'none';
  className?: string;
}

export default function BentoCard({
  icon, iconColor = '#00e479', title, badge, badgeColor,
  children, footer, className = '',
}: BentoCardProps) {
  return (
    <div
      className={`rounded p-3 flex flex-col gap-2 ${className}`}
      style={{ background: '#181c22', border: '1px solid rgba(59,75,61,0.3)' }}
    >
      {/* Header */}
      <div className="flex items-center justify-between text-label-md font-label-md text-[#dfe2eb]">
        <div className="flex items-center gap-1.5">
          {icon && <span className="material-symbols-outlined text-[16px]" style={{ color: iconColor }}>{icon}</span>}
          <span className="font-bold">{title}</span>
        </div>
        {badge && (
          <span
            className="text-label-sm font-label-sm px-1.5 py-0.5 rounded"
            style={badgeColor
              ? { background: `${badgeColor}15`, border: `1px solid ${badgeColor}50`, color: badgeColor }
              : { background: '#262a31', border: '1px solid rgba(59,75,61,0.4)', color: '#b9cbb9' }}
          >
            {badge}
          </span>
        )}
      </div>
      {/* Body */}
      <div className="flex-1">{children}</div>
      {/* Footer */}
      {footer && (
        <div className="pt-2 border-t text-label-sm font-label-sm text-[#849585]" style={{ borderColor: 'rgba(59,75,61,0.2)' }}>
          {footer}
        </div>
      )}
    </div>
  );
}
