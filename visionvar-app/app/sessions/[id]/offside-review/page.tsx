import AppShell from '@/components/layout/AppShell';
import BentoCard from '@/components/ui/BentoCard';
import StatusBadge from '@/components/ui/StatusBadge';
import { mockOffsideIncident } from '@/lib/mockData/offsideIncident';

export default function OffsideReviewPage() {
  const inc = mockOffsideIncident;
  const isOffside = inc.aiEstimation === 'OFFSIDE';

  return (
    <AppShell fullHeight>
      <div className="flex-1 flex flex-col lg:flex-row p-4 gap-4 overflow-hidden relative bg-[#0a0e14]">
        {/* Glow behind */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 rounded-full pointer-events-none opacity-20" style={{ background: isOffside ? '#ff3366' : '#00daf3', filter: 'blur(120px)' }} />

        {/* Video pane (Left) */}
        <div className="flex-1 relative rounded-lg overflow-hidden border flex flex-col justify-between" style={{ borderColor: isOffside ? 'rgba(255,51,102,0.4)' : 'rgba(0,218,243,0.4)' }}>
          {/* Main frame */}
          <div className="absolute inset-0 z-0 bg-black">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src="https://images.unsplash.com/photo-1579952363873-27f3bade9f55?q=80&w=2070&auto=format&fit=crop" alt="Pitch frame" className="w-full h-full object-cover opacity-60 grayscale" />
          </div>

          {/* SAOT laser planes */}
          <div className="absolute inset-0 z-10 pointer-events-none overflow-hidden perspective-1000">
            {/* Attacker plane */}
            <div
              className={`absolute top-0 bottom-0 w-1 ${isOffside ? 'laser-plane-red' : 'laser-plane-cyan'} z-20`}
              style={{ left: '42%', transform: 'rotateY(45deg)', transformOrigin: 'left' }}
            >
              <div className="absolute -top-6 -left-12 px-2 py-0.5 rounded text-[10px] font-mono font-bold tracking-widest text-[#0a0e14] whitespace-nowrap" style={{ background: isOffside ? '#ff3366' : '#00daf3' }}>
                ATT: {inc.attacker.axisMeters}m
              </div>
            </div>
            {/* Defender plane */}
            <div
              className="absolute top-0 bottom-0 w-1 bg-gradient-to-b from-[rgba(0,228,121,0.5)] to-transparent z-10 laser-line-green"
              style={{ left: '45%', transform: 'rotateY(45deg)', transformOrigin: 'left' }}
            >
               <div className="absolute -bottom-6 -left-12 px-2 py-0.5 rounded text-[10px] font-mono font-bold tracking-widest text-[#0a0e14] whitespace-nowrap bg-[#00e479]">
                DEF: {inc.defender.axisMeters}m
              </div>
            </div>
          </div>

          {/* Top HUD */}
          <div className="relative z-20 p-4 flex justify-between items-start">
             <div className="px-3 py-1.5 rounded-lg backdrop-blur-md border flex items-center gap-2" style={{ background: 'rgba(10,14,20,0.85)', borderColor: 'rgba(59,75,61,0.5)' }}>
               <span className="text-[#849585] text-label-sm font-label-sm">INCIDENT ID:</span>
               <span className="text-[#dfe2eb] text-label-md font-label-md font-mono">{inc.incidentId}</span>
             </div>
             <div className="flex flex-col gap-2 items-end">
               <StatusBadge label={inc.aiEstimation} color={isOffside ? 'crimson' : 'cyan'} pulse ping />
               <div className="px-2 py-1 rounded text-label-sm font-label-sm text-[#f1ffef]" style={{ background: 'rgba(10,14,20,0.85)', border: '1px solid rgba(59,75,61,0.5)' }}>
                 MARGIN: <span style={{ color: isOffside ? '#ffb4ab' : '#00daf3', fontWeight: 'bold' }}>{inc.marginMeters * 100}cm</span>
               </div>
             </div>
          </div>

          {/* Bottom Frame Stepper HUD */}
          <div className="relative z-20 p-4 w-full mt-auto bg-gradient-to-t from-[rgba(10,14,20,0.9)] to-transparent">
             <div className="flex justify-center gap-1">
               {/* Filmstrip mock */}
               {[-2, -1, 0, 1, 2].map((offset, i) => (
                 <div
                   key={i}
                   className="w-24 h-16 rounded overflow-hidden relative cursor-pointer transition-all hover:scale-105"
                   style={{
                     border: offset === 0 ? `2px solid ${isOffside ? '#ff3366' : '#00daf3'}` : '1px solid rgba(59,75,61,0.5)',
                     opacity: offset === 0 ? 1 : 0.6
                   }}
                 >
                   <div className="absolute inset-0 bg-[#262a31]" />
                   <div className="absolute bottom-0 w-full text-center text-[9px] font-mono font-bold bg-[rgba(10,14,20,0.8)] text-[#b9cbb9]">
                     F{inc.frameId + offset}
                     {offset === 0 && <span style={{ color: isOffside ? '#ff3366' : '#00daf3' }}> (LOCK)</span>}
                   </div>
                 </div>
               ))}
             </div>
          </div>
        </div>

        {/* Sidebar (Right) */}
        <div className="w-full lg:w-96 flex flex-col gap-4 overflow-y-auto">
          {/* Header Action */}
          <div className="flex justify-end gap-2">
            <button className="px-4 py-2 rounded text-label-md font-label-md font-bold hover:brightness-110 active:scale-95" style={{ background: '#262a31', color: '#b9cbb9', border: '1px solid rgba(59,75,61,0.4)' }}>
              OVERRIDE PITCH
            </button>
            <button className="px-4 py-2 rounded text-label-md font-label-md font-bold hover:brightness-110 active:scale-95" style={{ background: '#00e479', color: '#003919' }}>
              CONFIRM FRAME
            </button>
          </div>

          {/* Telemetry Summary */}
          <BentoCard title="SAOT Evaluation" icon="architecture" glowColor={isOffside ? 'none' : 'cyan'}>
             <div className="grid grid-cols-2 gap-2 mt-2">
                <div className="p-2 rounded bg-[#0a0e14] border border-[#3b4b3d]">
                  <div className="text-[10px] text-[#849585]">ATTACKER</div>
                  <div className="font-mono text-sm text-[#dfe2eb]">{inc.attacker.axisMeters}m</div>
                  <div className="text-[10px] text-[#00daf3] mt-1">{inc.attacker.bodyPartDatum}</div>
                </div>
                <div className="p-2 rounded bg-[#0a0e14] border border-[#3b4b3d]">
                  <div className="text-[10px] text-[#849585]">DEFENDER</div>
                  <div className="font-mono text-sm text-[#dfe2eb]">{inc.defender.axisMeters}m</div>
                  <div className="text-[10px] text-[#00e479] mt-1">{inc.defender.bodyPartDatum}</div>
                </div>
             </div>
             <div className="mt-3 p-2 rounded flex items-center justify-between font-mono" style={{ background: isOffside ? 'rgba(147,0,10,0.3)' : 'rgba(0,218,243,0.1)', border: `1px solid ${isOffside ? 'rgba(255,180,171,0.4)' : 'rgba(0,218,243,0.4)'}` }}>
               <span className="text-[11px]" style={{ color: isOffside ? '#ffdad6' : '#00daf3' }}>DELTA / MARGIN</span>
               <span className="font-bold text-sm" style={{ color: isOffside ? '#ffb4ab' : '#00daf3' }}>{inc.marginMeters * 100}cm</span>
             </div>
          </BentoCard>

          {/* Attacker Details */}
          <BentoCard title="Attacker Kinematics" icon="sprint">
             <div className="space-y-3 mt-2">
               <div className="flex justify-between items-center text-sm">
                 <span className="text-[#849585]">Player</span>
                 <span className="font-bold text-[#f1ffef]">{inc.attacker.jersey} {inc.attacker.name}</span>
               </div>
               <div className="flex justify-between items-center text-sm">
                 <span className="text-[#849585]">Velocity</span>
                 <span className="font-mono text-[#dfe2eb]">{inc.attacker.velocityKph} km/h</span>
               </div>
               <div className="flex justify-between items-center text-sm">
                 <span className="text-[#849585]">Acceleration</span>
                 <span className="font-mono text-[#dfe2eb]">{inc.attacker.accelerationMs2} m/s²</span>
               </div>
               <div className="flex justify-between items-center text-sm">
                 <span className="text-[#849585]">Body Lean Angle</span>
                 <span className="font-mono text-[#00daf3]">{inc.attacker.bodyLeanAngle}°</span>
               </div>
             </div>
          </BentoCard>

          {/* Ball Contact */}
          <BentoCard title="Kick Point Sync" icon="sports_soccer">
             <div className="space-y-3 mt-2">
               <div className="flex justify-between items-center text-sm">
                 <span className="text-[#849585]">Frame ID</span>
                 <span className="font-mono text-[#dfe2eb]">#{inc.ballContact.frameId}</span>
               </div>
               <div className="flex justify-between items-center text-sm">
                 <span className="text-[#849585]">Timecode</span>
                 <span className="font-mono text-[#dfe2eb]">{inc.ballContact.timecode}</span>
               </div>
               <div className="flex justify-between items-center text-sm">
                 <span className="text-[#849585]">Ball Speed</span>
                 <span className="font-mono text-[#00e479]">{inc.ballContact.ballSpeedKph} km/h</span>
               </div>
               <div className="flex items-center gap-2 mt-2 p-1.5 rounded bg-[rgba(0,228,121,0.1)] border border-[rgba(0,228,121,0.3)]">
                  <span className="material-symbols-outlined text-[14px] text-[#00e479]">verified</span>
                  <span className="text-[11px] text-[#00e479] font-bold">CONTACT CONFIRMED</span>
               </div>
             </div>
          </BentoCard>

        </div>
      </div>
    </AppShell>
  );
}
