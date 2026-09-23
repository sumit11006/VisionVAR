import AppShell from '@/components/layout/AppShell';
import BentoCard from '@/components/ui/BentoCard';
import PitchSVGRadar from '@/components/radar/PitchSVGRadar';
import { teamACentroidsRadar, teamBCentroidsRadar } from '@/lib/mockData/players';

export default function FormationRadarPage() {
  return (
    <AppShell fullHeight>
      <div className="flex-1 flex p-4 gap-4 overflow-hidden relative">

        {/* Left pane: Team A (Cyan) */}
        <div className="w-64 flex flex-col gap-4 overflow-y-auto pr-2">
           <div className="flex items-center justify-between pb-2" style={{ borderBottom: '1px solid rgba(0,218,243,0.3)' }}>
              <h2 className="text-headline-md font-headline-md text-[#f1ffef]">Manchester City</h2>
              <span className="text-label-sm font-label-sm px-2 py-0.5 rounded bg-[rgba(0,218,243,0.15)] text-[#00daf3]">4-2-3-1</span>
           </div>
           
           <BentoCard title="Avg Positional Block" icon="group_work" glowColor="cyan">
             <div className="flex flex-col gap-2 font-mono text-sm mt-2">
                <div className="flex justify-between text-[#b9cbb9]"><span>Defensive Line</span><span className="text-[#dfe2eb]">42.4m</span></div>
                <div className="flex justify-between text-[#b9cbb9]"><span>Team Length</span><span className="text-[#dfe2eb]">31.2m</span></div>
                <div className="flex justify-between text-[#b9cbb9]"><span>Team Width</span><span className="text-[#dfe2eb]">48.6m</span></div>
             </div>
           </BentoCard>

           <div className="text-label-sm font-label-sm text-[#849585] uppercase tracking-wider mt-2">Key Players</div>
           {[
             { num: 9, name: 'Haaland', stat: 'Top Speed: 35.8 km/h' },
             { num: 17, name: 'De Bruyne', stat: 'Distance: 9.14 km' },
             { num: 16, name: 'Rodri', stat: 'Central Presence: 84%' },
           ].map(p => (
             <div key={p.num} className="p-2 rounded bg-[rgba(28,32,38,0.5)] border border-[rgba(59,75,61,0.4)] flex items-center gap-3">
               <div className="w-8 h-8 rounded bg-[rgba(0,218,243,0.1)] border border-[rgba(0,218,243,0.4)] text-[#00daf3] font-bold flex items-center justify-center font-mono text-sm">{p.num}</div>
               <div>
                 <div className="text-sm font-bold text-[#dfe2eb]">{p.name}</div>
                 <div className="text-[10px] text-[#849585]">{p.stat}</div>
               </div>
             </div>
           ))}
        </div>

        {/* Center pane: The Radar */}
        <div className="flex-1 rounded-xl p-6 relative overflow-hidden flex flex-col tactical-grid-bg" style={{ border: '1px solid rgba(59,75,61,0.5)', background: '#0a0e14' }}>
          {/* Header */}
          <div className="flex justify-between items-start relative z-10 mb-4">
             <div className="flex items-center gap-3">
                <span className="px-3 py-1 rounded bg-[rgba(10,14,20,0.8)] border border-[#3b4b3d] text-label-sm font-label-sm text-[#b9cbb9] backdrop-blur">
                  LIVE TRACKING
                </span>
                <span className="px-3 py-1 rounded bg-[rgba(10,14,20,0.8)] border border-[#3b4b3d] text-label-sm font-label-sm text-[#00e479] flex items-center gap-1.5 backdrop-blur">
                  <span className="w-1.5 h-1.5 bg-[#00e479] rounded-full animate-ping" /> REAL-TIME 120Hz
                </span>
             </div>
             <div className="flex gap-2">
                {['HEATMAP', 'VORONOI', 'PASS NET'].map(t => (
                  <button key={t} className="px-3 py-1 rounded text-label-sm font-label-sm text-[#849585] border border-[#3b4b3d] bg-[rgba(10,14,20,0.8)] hover:text-[#dfe2eb] transition-all">
                    {t}
                  </button>
                ))}
             </div>
          </div>

          {/* Large Pitch */}
          <div className="flex-1 w-full h-full relative radar-pitch rounded-lg border border-[rgba(59,75,61,0.5)] overflow-hidden">
             {/* 2D pitch mapping mock - stretching the mini radar to fit */}
             <div className="absolute inset-4">
               <PitchSVGRadar teamADots={teamACentroidsRadar} teamBDots={teamBCentroidsRadar} height="h-full" />
             </div>

             {/* Overlays */}
             <div className="absolute top-1/2 left-[20%] w-32 h-64 -translate-y-1/2 border border-dashed border-[#00daf3] rounded opacity-30 bg-[rgba(0,218,243,0.05)] pointer-events-none" />
             <div className="absolute top-1/2 right-[20%] w-32 h-64 -translate-y-1/2 border border-dashed border-[#00e479] rounded opacity-30 bg-[rgba(0,228,121,0.05)] pointer-events-none" />
          </div>

          <div className="mt-4 flex justify-between items-center text-label-sm text-[#849585]">
             <span>Phase: Build-up Play</span>
             <span>Possession: MCI 58% - 42% RMA</span>
          </div>
        </div>

        {/* Right pane: Team B (Emerald) */}
        <div className="w-64 flex flex-col gap-4 overflow-y-auto pl-2">
           <div className="flex items-center justify-between pb-2" style={{ borderBottom: '1px solid rgba(0,228,121,0.3)' }}>
              <h2 className="text-headline-md font-headline-md text-[#f1ffef]">Real Madrid</h2>
              <span className="text-label-sm font-label-sm px-2 py-0.5 rounded bg-[rgba(0,228,121,0.15)] text-[#00e479]">4-3-3</span>
           </div>
           
           <BentoCard title="Avg Positional Block" icon="group_work" glowColor="emerald">
             <div className="flex flex-col gap-2 font-mono text-sm mt-2">
                <div className="flex justify-between text-[#b9cbb9]"><span>Defensive Line</span><span className="text-[#dfe2eb]">36.8m</span></div>
                <div className="flex justify-between text-[#b9cbb9]"><span>Team Length</span><span className="text-[#dfe2eb]">34.5m</span></div>
                <div className="flex justify-between text-[#b9cbb9]"><span>Team Width</span><span className="text-[#dfe2eb]">45.2m</span></div>
             </div>
           </BentoCard>

           <div className="text-label-sm font-label-sm text-[#849585] uppercase tracking-wider mt-2">Key Players</div>
           {[
             { num: 7, name: 'Vinícius Jr.', stat: 'Top Speed: 36.4 km/h' },
             { num: 5, name: 'Bellingham', stat: 'Distance: 9.85 km' },
             { num: 10, name: 'Modrić', stat: 'Pass Acc: 94%' },
           ].map(p => (
             <div key={p.num} className="p-2 rounded bg-[rgba(28,32,38,0.5)] border border-[rgba(59,75,61,0.4)] flex items-center gap-3">
               <div className="w-8 h-8 rounded bg-[rgba(0,228,121,0.1)] border border-[rgba(0,228,121,0.4)] text-[#00e479] font-bold flex items-center justify-center font-mono text-sm">{p.num}</div>
               <div>
                 <div className="text-sm font-bold text-[#dfe2eb]">{p.name}</div>
                 <div className="text-[10px] text-[#849585]">{p.stat}</div>
               </div>
             </div>
           ))}
        </div>

      </div>
    </AppShell>
  );
}
