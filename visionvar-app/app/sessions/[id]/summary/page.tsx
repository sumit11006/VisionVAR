'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import AppShell from '@/components/layout/AppShell';
import BentoCard from '@/components/ui/BentoCard';
import StatusBadge from '@/components/ui/StatusBadge';
import { mockMatch } from '@/lib/mockData/match';
import { fetchMatch } from '@/lib/api';
import type { MatchContext } from '@/types';

export default function MatchSummaryPage() {
  const params = useParams();
  const matchId = (params?.id as string) || mockMatch.id;
  const [match, setMatch] = useState<MatchContext>(mockMatch);

  useEffect(() => {
    fetchMatch(matchId)
      .then((data) => {
        if (data) setMatch(data);
      })
      .catch(() => {
        // Graceful fallback to mockMatch
      });
  }, [matchId]);
  return (
    <AppShell fullHeight>
      <div className="flex-1 flex flex-col p-4 gap-6 overflow-hidden relative bg-[#0a0e14] overflow-y-auto">
        
        {/* Glow Effects */}
        <div className="absolute top-0 right-0 w-[50vw] h-[50vh] bg-gradient-to-bl from-[rgba(0,218,243,0.05)] to-transparent pointer-events-none rounded-bl-full" />
        <div className="absolute top-0 left-0 w-[50vw] h-[50vh] bg-gradient-to-br from-[rgba(0,228,121,0.05)] to-transparent pointer-events-none rounded-br-full" />

        {/* Scoreboard Header */}
        <div className="flex flex-col items-center justify-center py-8 relative z-10">
           <div className="text-label-sm font-label-sm text-[#849585] mb-2">{match.competition} • {match.venue}</div>
           
           <div className="flex items-center gap-12">
             <div className="flex flex-col items-center gap-4">
                <div className="w-24 h-24 rounded-full bg-[rgba(28,32,38,0.8)] border-2 border-[rgba(0,218,243,0.5)] flex items-center justify-center overflow-hidden">
                   {/* Team Logo Placeholder */}
                   <span className="text-3xl font-headline-lg font-bold text-[#00daf3]">{match.homeTeam.code}</span>
                </div>
                <h2 className="text-headline-md font-headline-md text-[#f1ffef]">{match.homeTeam.name}</h2>
             </div>

             <div className="flex flex-col items-center gap-2">
                <div className="text-display-xl font-display-xl font-bold tracking-tighter text-[#f1ffef] flex items-center gap-4">
                  <span>{match.score.home}</span>
                  <span className="text-[#3b4b3d]">-</span>
                  <span>{match.score.away}</span>
                </div>
                <StatusBadge label={`${match.period} • ${match.clock}`} color="emerald" pulse />
             </div>

             <div className="flex flex-col items-center gap-4">
                <div className="w-24 h-24 rounded-full bg-[rgba(28,32,38,0.8)] border-2 border-[rgba(0,228,121,0.5)] flex items-center justify-center overflow-hidden">
                   {/* Team Logo Placeholder */}
                   <span className="text-3xl font-headline-lg font-bold text-[#00e479]">{match.awayTeam.code}</span>
                </div>
                <h2 className="text-headline-md font-headline-md text-[#f1ffef]">{match.awayTeam.name}</h2>
             </div>
           </div>
        </div>

        {/* Post-Match AI Summary & Stats */}
        <div className="max-w-6xl mx-auto w-full grid grid-cols-1 md:grid-cols-3 gap-6 relative z-10 pb-12">
           
           <div className="col-span-2 flex flex-col gap-6">
              <BentoCard title="AI Match Narrative" icon="psychology">
                 <div className="text-body-md text-[#b9cbb9] leading-relaxed mt-2 space-y-4">
                   <p>
                     VisionVAR neural analysis indicates a highly contested midfield battle characterized by rapid transitional phases. Manchester City established early dominance in possession (58%), primarily channeling attacks through the left half-spaces via Grealish and De Bruyne.
                   </p>
                   <p>
                     Real Madrid maintained a disciplined mid-block (Avg defensive line: 36.8m), successfully neutralizing 4 high-danger penetrations. Vinícius Jr. provided consistent counter-attacking threat, resulting in 3 key VAR-reviewed incidents.
                   </p>
                   <div className="p-3 rounded bg-[rgba(10,14,20,0.6)] border border-[rgba(59,75,61,0.4)] flex items-start gap-3 mt-4">
                     <span className="material-symbols-outlined text-[#00daf3]">insights</span>
                     <div>
                       <div className="text-sm font-bold text-[#dfe2eb]">Key Insight: Expected Goals (xG) Overperformance</div>
                       <div className="text-xs text-[#849585] mt-1">
                         MCI registered 1.42 xG vs 2 actual goals (+0.58). RMA registered 0.84 xG vs 1 actual goal (+0.16). Clinical finishing in low-probability scenarios was the deciding factor.
                       </div>
                     </div>
                   </div>
                 </div>
              </BentoCard>

              {/* VAR Incident Summary */}
              <BentoCard title="VAR Intervention Log" icon="flag">
                 <div className="grid grid-cols-3 gap-4 mt-2">
                    <div className="p-4 rounded border border-[rgba(59,75,61,0.4)] bg-[rgba(28,32,38,0.4)] text-center flex flex-col gap-1">
                       <span className="text-2xl font-mono font-bold text-[#00daf3]">14</span>
                       <span className="text-[10px] text-[#849585] uppercase tracking-wider">Total Checks</span>
                    </div>
                    <div className="p-4 rounded border border-[rgba(0,228,121,0.4)] bg-[rgba(0,228,121,0.05)] text-center flex flex-col gap-1">
                       <span className="text-2xl font-mono font-bold text-[#00e479]">3</span>
                       <span className="text-[10px] text-[#849585] uppercase tracking-wider">Interventions</span>
                    </div>
                    <div className="p-4 rounded border border-[rgba(255,180,171,0.4)] bg-[rgba(147,0,10,0.2)] text-center flex flex-col gap-1">
                       <span className="text-2xl font-mono font-bold text-[#ffb4ab]">1</span>
                       <span className="text-[10px] text-[#849585] uppercase tracking-wider">Overturns</span>
                    </div>
                 </div>
                 <div className="mt-4 pt-4 border-t border-[rgba(59,75,61,0.3)]">
                    <div className="text-label-sm text-[#849585] mb-2">Major Overturn: Penalty Rescinded (34&apos;)</div>
                    <div className="text-body-sm text-[#b9cbb9]">Initial penalty award to Erling Haaland was overturned after AI impact analysis confirmed contact force was minimal (below 4G threshold) and occurred 2.4cm outside the penalty area by reprojection.</div>
                 </div>
              </BentoCard>
           </div>

           <div className="flex flex-col gap-6">
              <BentoCard title="Match Statistics" icon="bar_chart">
                 <div className="flex flex-col gap-4 mt-4">
                    {[
                      { label: 'Possession', valA: '58%', valB: '42%', pctA: 58 },
                      { label: 'Shots (On Target)', valA: '14 (6)', valB: '9 (3)', pctA: 60 },
                      { label: 'Expected Goals (xG)', valA: '1.42', valB: '0.84', pctA: 63 },
                      { label: 'Pass Accuracy', valA: '89%', valB: '84%', pctA: 51 },
                      { label: 'Distance Covered (km)', valA: '114.2', valB: '112.8', pctA: 50 },
                    ].map((stat, i) => (
                      <div key={i} className="flex flex-col gap-1.5">
                         <div className="flex justify-between text-sm font-mono">
                            <span className="text-[#00daf3]">{stat.valA}</span>
                            <span className="text-[#849585] text-xs font-sans tracking-wide">{stat.label}</span>
                            <span className="text-[#00e479]">{stat.valB}</span>
                         </div>
                         <div className="w-full h-1.5 rounded-full bg-[rgba(28,32,38,0.8)] overflow-hidden flex">
                            <div className="h-full bg-[#00daf3]" style={{ width: `${stat.pctA}%` }} />
                            <div className="h-full bg-[#00e479]" style={{ width: `${100 - stat.pctA}%` }} />
                         </div>
                      </div>
                    ))}
                 </div>
              </BentoCard>

              <BentoCard title="AI Performance" icon="memory">
                 <div className="flex flex-col gap-3 mt-2 font-mono text-sm">
                   <div className="flex justify-between border-b border-[rgba(59,75,61,0.2)] pb-2">
                     <span className="text-[#849585]">Avg Latency</span>
                     <span className="text-[#00e479]">12.4ms</span>
                   </div>
                   <div className="flex justify-between border-b border-[rgba(59,75,61,0.2)] pb-2">
                     <span className="text-[#849585]">Tracking Uptime</span>
                     <span className="text-[#dfe2eb]">99.98%</span>
                   </div>
                   <div className="flex justify-between">
                     <span className="text-[#849585]">Data Points Generated</span>
                     <span className="text-[#dfe2eb]">18.4M</span>
                   </div>
                 </div>
              </BentoCard>
           </div>
        </div>

      </div>
    </AppShell>
  );
}
