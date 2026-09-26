import type { PipelineStage } from '@/types';

export default function PipelineStageCard({ stage }: { stage: PipelineStage }) {
  const isComplete = stage.status === 'COMPLETE';
  const isActive   = stage.status === 'ACTIVE';

  const borderColor = isComplete ? 'rgba(0,228,121,0.4)' : isActive ? '#00daf3' : 'rgba(59,75,61,0.3)';
  const labelColor  = isComplete ? '#00e479' : isActive ? '#00daf3' : '#849585';
  const shadow      = isActive ? '0 0 14px rgba(0,218,243,0.15)' : 'none';
  const borderWidth = isActive ? '2px' : '1px';

  return (
    <div
      className="p-3.5 rounded-lg flex flex-col justify-between h-36 relative overflow-hidden"
      style={{ background: '#0a0e14', border: `${borderWidth} solid ${borderColor}`, boxShadow: shadow }}
    >
      {isActive && (
        <span
          className="absolute top-0 right-0 px-1.5 py-0.5 text-[#0a0e14] text-label-sm font-label-sm font-bold tracking-wider"
          style={{ background: '#00daf3' }}
        >
          ACTIVE
        </span>
      )}
      <div className="flex items-center justify-between">
        <span className="text-label-sm font-label-sm text-[#b9cbb9]">STAGE 0{stage.stage}</span>
        <span className="text-label-sm font-label-sm font-bold flex items-center gap-1 mr-8" style={{ color: labelColor }}>
          {isComplete && <span className="material-symbols-outlined text-[13px]" style={{ fontVariationSettings: "'FILL' 1" }}>check_circle</span>}
          {stage.progress}%
        </span>
      </div>
      <div>
        <h3 className="text-label-md font-label-md font-semibold text-[#f1ffef] flex items-center gap-1.5">
          {stage.label}
          {isActive && <span className="w-1.5 h-1.5 rounded-full bg-[#00daf3] animate-ping" />}
        </h3>
        <p className="text-body-sm font-body-sm text-[#b9cbb9] mt-0.5" style={{ fontSize: '10px' }}>{stage.detail}</p>
      </div>
      {/* Progress bar */}
      <div className="w-full h-1.5 rounded-full overflow-hidden" style={{ background: '#262a31' }}>
        <div
          className="h-full rounded-full transition-all duration-300"
          style={{ width: `${stage.progress}%`, background: labelColor }}
        />
      </div>
    </div>
  );
}
