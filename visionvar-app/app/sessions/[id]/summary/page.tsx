'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import AppShell from '@/components/layout/AppShell';
import BentoCard from '@/components/ui/BentoCard';
import StatusBadge from '@/components/ui/StatusBadge';
import { MatchEvent } from '@/types';
import { fetchMatch, fetchMatchSummary } from '@/lib/api';
import type { MatchContext } from '@/types';

export default function MatchSummaryPage() {
  const params = useParams();
  const matchId = (params?.id as string) || '';
  const [match, setMatch] = useState<MatchContext | null>(null);
  const [summary, setSummary] = useState<any>(null);

  useEffect(() => {
    fetchMatch(matchId)
      .then((data) => {
        if (data) setMatch(data);
      })
      .catch((err) => {
        console.error("Failed to load match", err);
      });
      
    fetchMatchSummary(matchId)
      .then((data) => {
        if (data && Object.keys(data).length > 0) setSummary(data);
      })
      .catch(console.error);
  }, [matchId]);

  if (!match) return <div className="p-8 text-[#849585]">Loading match data...</div>;

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
                   {summary && summary.tactical_insights && summary.tactical_insights.length > 0 ? (
                     summary.tactical_insights.map((insight: string, idx: number) => (
                       <div key={idx} className="p-3 rounded bg-[rgba(10,14,20,0.6)] border border-[rgba(59,75,61,0.4)] flex items-start gap-3 mt-4">
                         <span className="material-symbols-outlined text-[#00daf3]">insights</span>
                         <div>
                           <div className="text-sm font-bold text-[#dfe2eb]">AI Observation {idx + 1}</div>
                           <div className="text-xs text-[#849585] mt-1">{insight}</div>
                         </div>
                       </div>
                     ))
                   ) : (
                     <div className="text-[#849585]">Insufficient evidence for tactical insights. Run a detection pipeline to generate actual statistics.</div>
                   )}
                 </div>
              </BentoCard>

              {/* VAR Incident Summary */}
              <BentoCard title="AI Event Log" icon="flag">
                 <div className="grid grid-cols-3 gap-4 mt-2">
                    <div className="p-4 rounded border border-[rgba(59,75,61,0.4)] bg-[rgba(28,32,38,0.4)] text-center flex flex-col gap-1">
                       <span className="text-2xl font-mono font-bold text-[#00daf3]">
                         {summary ? summary.event_summary.goals.confirmed + summary.event_summary.shots.confirmed + summary.event_summary.passes.confirmed + summary.event_summary.offside_candidates + summary.event_summary.turnovers.confirmed : 'Not available'}
                       </span>
                       <span className="text-[10px] text-[#849585] uppercase tracking-wider">Total Events</span>
                    </div>
                    <div className="p-4 rounded border border-[rgba(0,228,121,0.4)] bg-[rgba(0,228,121,0.05)] text-center flex flex-col gap-1">
                       <span className="text-2xl font-mono font-bold text-[#00e479]">
                         {summary ? summary.event_summary.goals.confirmed : 'Not available'}
                       </span>
                       <span className="text-[10px] text-[#849585] uppercase tracking-wider">Goals (Confirmed)</span>
                    </div>
                    <div className="p-4 rounded border border-[rgba(255,180,171,0.4)] bg-[rgba(147,0,10,0.2)] text-center flex flex-col gap-1">
                       <span className="text-2xl font-mono font-bold text-[#ffb4ab]">
                         {summary ? summary.event_summary.offside_candidates : 'Not available'}
                       </span>
                       <span className="text-[10px] text-[#849585] uppercase tracking-wider">Offside Candidates</span>
                    </div>
                 </div>
                 <div className="mt-4 pt-4 border-t border-[rgba(59,75,61,0.3)]">
                    <div className="text-label-sm text-[#849585] mb-2">Automated Event Pipeline</div>
                    <div className="text-body-sm text-[#b9cbb9]">Counts above reflect aggregated occurrences from persisted ML detection layers (Ball/Offside/Goals) run via VisionVAR CV architecture.</div>
                 </div>
              </BentoCard>
           </div>

           <div className="flex flex-col gap-6">
              <BentoCard title="Match Statistics" icon="bar_chart">
                 <div className="flex flex-col gap-4 mt-4">
                    {!summary ? (
                      <div className="text-[#849585] text-sm">Not available (Run detection first)</div>
                    ) : (
                      <>
                        {[
                          { label: 'Possession', valA: `${summary.possession[match.homeTeam.code] || 0}%`, valB: `${summary.possession[match.awayTeam.code] || 0}%`, pctA: summary.possession[match.homeTeam.code] || 50 },
                          { label: 'Passes', valA: summary.team_analytics.find((t: any) => t.team_name === match.homeTeam.code)?.passes || 0, valB: summary.team_analytics.find((t: any) => t.team_name === match.awayTeam.code)?.passes || 0, pctA: 50 },
                          { label: 'Shots', valA: summary.team_analytics.find((t: any) => t.team_name === match.homeTeam.code)?.shots || 0, valB: summary.team_analytics.find((t: any) => t.team_name === match.awayTeam.code)?.shots || 0, pctA: 50 },
                          { label: 'Distance Covered (km)', valA: (summary.team_analytics.find((t: any) => t.team_name === match.homeTeam.code)?.estimated_distance_m / 1000 || 0).toFixed(2), valB: (summary.team_analytics.find((t: any) => t.team_name === match.awayTeam.code)?.estimated_distance_m / 1000 || 0).toFixed(2), pctA: 50 },
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
                      </>
                    )}
                 </div>
              </BentoCard>

              <BentoCard title="Data Quality & Performance" icon="memory">
                 <div className="flex flex-col gap-3 mt-2 font-mono text-sm">
                   {summary ? (
                     <>
                       <div className="flex justify-between border-b border-[rgba(59,75,61,0.2)] pb-2">
                         <span className="text-[#849585]">Tracking Uptime</span>
                         <span className="text-[#00e479]">{summary.data_quality.known_team_samples_percentage}%</span>
                       </div>
                       <div className="flex justify-between border-b border-[rgba(59,75,61,0.2)] pb-2">
                         <span className="text-[#849585]">Track IDs Used</span>
                         <span className="text-[#dfe2eb]">{summary.data_quality.unique_track_ids}</span>
                       </div>
                       <div className="flex justify-between">
                         <span className="text-[#849585]">Data Points Generated</span>
                         <span className="text-[#dfe2eb]">{summary.data_quality.mapped_samples}</span>
                       </div>
                     </>
                   ) : (
                     <div className="text-[#849585]">Not available</div>
                   )}
                 </div>
              </BentoCard>
           </div>
        </div>

      </div>
    </AppShell>
  );
}
