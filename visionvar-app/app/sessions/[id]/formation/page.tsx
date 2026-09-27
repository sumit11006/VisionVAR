'use client';

import { useState, useEffect, useRef } from 'react';
import { useParams } from 'next/navigation';
import AppShell from '@/components/layout/AppShell';
import BentoCard from '@/components/ui/BentoCard';
import PitchSVGRadar from '@/components/radar/PitchSVGRadar';
import { connectAnalysisWebSocket, TrackedItem, FrameTrackingMessage } from '@/lib/api';

export default function FormationRadarPage() {
  const params = useParams();
  const sessionId = (params?.id as string) || 'UCL-2024-MCI-RMA-F';

  const [trackedItems, setTrackedItems] = useState<TrackedItem[]>([]);
  const [formationData, setFormationData] = useState<{team_a: string, team_b: string, confidence: number} | null>(null);
  const [ballData, setBallData] = useState<any>(null);

  useEffect(() => {
    const ws = connectAnalysisWebSocket(
      sessionId,
      (data) => {
        if (data.type === 'frame_tracking') {
          const msg = data as unknown as FrameTrackingMessage & { formation?: any };
          if (msg.tracked_items) {
            setTrackedItems(msg.tracked_items);
          }
          if (msg.formation) {
            setFormationData(msg.formation);
          }
          if (msg.ball) {
            setBallData(msg.ball);
          }
        }
      }
    );

    return () => {
      ws.close();
    };
  }, [sessionId]);

  const pitchToSvgX = (x: number) => 2 + (x / 105) * 296;
  const pitchToSvgY = (y: number) => 2 + (y / 68) * 156;

  const teamADots = trackedItems
    .filter((d) => d.class === 'player' && d.team === 'team_a' && d.pitch_position && d.mapping_status === 'mapped')
    .map((d) => ({ 
      cx: pitchToSvgX(d.pitch_position!.x), 
      cy: pitchToSvgY(d.pitch_position!.y), 
      active: true,
      trail: d.movement_trail ? d.movement_trail.map(t => ({ cx: pitchToSvgX(t[0]), cy: pitchToSvgY(t[1]) })) : []
    }));

  const teamBDots = trackedItems
    .filter((d) => d.class === 'player' && d.team === 'team_b' && d.pitch_position && d.mapping_status === 'mapped')
    .map((d) => ({ 
      cx: pitchToSvgX(d.pitch_position!.x), 
      cy: pitchToSvgY(d.pitch_position!.y),
      trail: d.movement_trail ? d.movement_trail.map(t => ({ cx: pitchToSvgX(t[0]), cy: pitchToSvgY(t[1]) })) : []
    }));

  const mappedBall = (ballData && ballData.pitch_position && ballData.state === 'tracked')
    ? { 
        cx: pitchToSvgX(ballData.pitch_position.x), 
        cy: pitchToSvgY(ballData.pitch_position.y),
        trail: ballData.movement_trail ? ballData.movement_trail.map((t: number[]) => ({ cx: pitchToSvgX(t[0]), cy: pitchToSvgY(t[1]) })) : []
      }
    : undefined;

  const isMapped = trackedItems.some(d => d.mapping_status === 'mapped');
  const teamAFormation = formationData?.team_a || 'Unknown';
  const teamBFormation = formationData?.team_b || 'Unknown';
  const formationConf = formationData?.confidence ? `${Math.round(formationData.confidence * 100)}%` : '0%';

  return (
    <AppShell fullHeight>
      <div className="flex-1 flex p-4 gap-4 overflow-hidden relative">

        {/* Left pane: Team A (Cyan) */}
        <div className="w-64 flex flex-col gap-4 overflow-y-auto pr-2">
           <div className="flex items-center justify-between pb-2" style={{ borderBottom: '1px solid rgba(0,218,243,0.3)' }}>
              <h2 className="text-headline-md font-headline-md text-[#f1ffef]">Team A</h2>
              <span className="text-label-sm font-label-sm px-2 py-0.5 rounded bg-[rgba(0,218,243,0.15)] text-[#00daf3]">{teamAFormation}</span>
           </div>
           
           <BentoCard title="Formation Analytics" icon="group_work" glowColor="cyan">
             <div className="flex flex-col gap-2 font-mono text-sm mt-2">
                <div className="flex justify-between text-[#b9cbb9]"><span>Confidence</span><span className="text-[#dfe2eb]">{formationConf}</span></div>
                <div className="flex justify-between text-[#b9cbb9]"><span>Players Tracked</span><span className="text-[#dfe2eb]">{teamADots.length}</span></div>
                <div className="flex justify-between text-[#b9cbb9]"><span>Mapping Status</span><span className="text-[#dfe2eb]">{isMapped ? 'Active' : 'Unavailable'}</span></div>
             </div>
           </BentoCard>

           <BentoCard title="Ball Tracking" icon="sports_soccer">
             <div className="flex flex-col gap-2 font-mono text-sm mt-2">
                <div className="flex justify-between text-[#b9cbb9]"><span>Status</span><span className="text-[#dfe2eb]">{ballData && (ballData.state === 'tracked' || ballData.state === 'reacquired') ? 'VISIBLE' : 'NOT VISIBLE'}</span></div>
                <div className="flex justify-between text-[#b9cbb9]"><span>Confidence</span><span className="text-[#dfe2eb]">{ballData?.confidence ? `${Math.round(ballData.confidence * 100)}%` : '0%'}</span></div>
                <div className="flex justify-between text-[#b9cbb9]"><span>Projected</span><span className="text-[#dfe2eb]">{ballData?.pitch_position ? 'YES' : 'NO'}</span></div>
             </div>
           </BentoCard>
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
          </div>

          {/* Large Pitch */}
          <div className="flex-1 w-full h-full relative radar-pitch rounded-lg border border-[rgba(59,75,61,0.5)] overflow-hidden">
             <div className="absolute inset-4">
               <PitchSVGRadar teamADots={teamADots} teamBDots={teamBDots} ballPos={mappedBall} height="h-full" />
             </div>
          </div>
        </div>

        {/* Right pane: Team B (Emerald) */}
        <div className="w-64 flex flex-col gap-4 overflow-y-auto pl-2">
           <div className="flex items-center justify-between pb-2" style={{ borderBottom: '1px solid rgba(0,228,121,0.3)' }}>
              <h2 className="text-headline-md font-headline-md text-[#f1ffef]">Team B</h2>
              <span className="text-label-sm font-label-sm px-2 py-0.5 rounded bg-[rgba(0,228,121,0.15)] text-[#00e479]">{teamBFormation}</span>
           </div>
           
           <BentoCard title="Formation Analytics" icon="group_work" glowColor="emerald">
             <div className="flex flex-col gap-2 font-mono text-sm mt-2">
                <div className="flex justify-between text-[#b9cbb9]"><span>Confidence</span><span className="text-[#dfe2eb]">{formationConf}</span></div>
                <div className="flex justify-between text-[#b9cbb9]"><span>Players Tracked</span><span className="text-[#dfe2eb]">{teamBDots.length}</span></div>
                <div className="flex justify-between text-[#b9cbb9]"><span>Mapping Status</span><span className="text-[#dfe2eb]">{isMapped ? 'Active' : 'Unavailable'}</span></div>
             </div>
           </BentoCard>
        </div>

      </div>
    </AppShell>
  );
}
