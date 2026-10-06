'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import AppShell from '@/components/layout/AppShell';
import BentoCard from '@/components/ui/BentoCard';
import StatusBadge from '@/components/ui/StatusBadge';
import { connectAnalysisWebSocket, FrameTrackingMessage, OffsideCandidate, fetchMatchEvents } from '@/lib/api';

export default function OffsideReviewPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = (params?.id as string) || 'UCL-2024-MCI-RMA-F';

  const [candidate, setCandidate] = useState<OffsideCandidate | null>(null);
  const [frameId, setFrameId] = useState<number>(0);
  const [timestamp, setTimestamp] = useState<number>(0);

  useEffect(() => {
    // 1. Fetch historical offside candidate if analysis already finished
    fetchMatchEvents(sessionId)
      .then(events => {
        if (events && events.length > 0) {
          const offsideEvents = events.filter(e => e.type === 'OFFSIDE_CANDIDATE');
          if (offsideEvents.length > 0) {
            const latest = offsideEvents[offsideEvents.length - 1];
            if (latest.metadata_json) {
              try {
                const offsideData = JSON.parse(latest.metadata_json) as OffsideCandidate;
                setCandidate(offsideData);
                setFrameId(latest.frameId || 0);
                setTimestamp((latest.minute * 60) + latest.second);
              } catch (e) {}
            }
          }
        }
      })
      .catch(() => {});

    // 2. Connect live WebSocket
    const ws = connectAnalysisWebSocket(
      sessionId,
      (data) => {
        if (data.type === 'frame_tracking') {
          const msg = data as unknown as FrameTrackingMessage;
          if (msg.offside && msg.offside.status === 'candidate') {
            setCandidate(msg.offside);
            setFrameId(msg.frame);
            setTimestamp(msg.timestamp);
          }
        }
      }
    );

    return () => {
      ws.close();
    };
  }, [sessionId]);

  const hasEvidence = candidate?.status === 'candidate' && candidate.ai_assessment !== 'INSUFFICIENT EVIDENCE';
  const isOffside = candidate?.ai_assessment === 'POTENTIAL OFFSIDE';
  
  const statusLabel = candidate?.ai_assessment || 'WAITING FOR DATA';

  return (
    <AppShell fullHeight>
      <div className="flex-1 flex flex-col lg:flex-row p-4 gap-4 overflow-hidden relative bg-[#0a0e14]">
        {/* Glow behind */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 rounded-full pointer-events-none opacity-20" style={{ background: isOffside ? '#ff3366' : '#00daf3', filter: 'blur(120px)' }} />

        {/* Video pane (Left) */}
        <div className="flex-1 relative rounded-lg overflow-hidden border flex flex-col justify-between" style={{ borderColor: isOffside ? 'rgba(255,51,102,0.4)' : 'rgba(0,218,243,0.4)' }}>
          {/* Main frame */}
          <div className="absolute inset-0 z-0 bg-black flex items-center justify-center">
            <span className="text-[#849585] text-lg font-mono">
              {candidate ? `Candidate Frame: ${frameId}` : "Waiting for candidate frame..."}
            </span>
          </div>

          {/* Top HUD */}
          <div className="relative z-20 p-4 flex justify-between items-start">
             <div className="px-3 py-1.5 rounded-lg backdrop-blur-md border flex items-center gap-2" style={{ background: 'rgba(10,14,20,0.85)', borderColor: 'rgba(59,75,61,0.5)' }}>
               <span className="text-[#849585] text-label-sm font-label-sm">AI ASSESSMENT:</span>
               <span className="text-[#dfe2eb] text-label-md font-label-md font-mono">FRAME {frameId}</span>
             </div>
             <div className="flex flex-col gap-2 items-end">
               {candidate && (
                 <StatusBadge label={statusLabel} color={isOffside ? 'crimson' : (hasEvidence ? 'cyan' : 'amber')} pulse ping />
               )}
             </div>
          </div>
        </div>

        {/* Sidebar (Right) */}
        <div className="w-full lg:w-96 flex flex-col gap-4 overflow-y-auto">
          {/* Header Action */}
          <div className="flex justify-end gap-2">
            <button 
              onClick={() => router.push(`/sessions/${sessionId}?t=${timestamp}`)}
              className="px-4 py-2 rounded text-label-md font-label-md font-bold hover:brightness-110 active:scale-95" style={{ background: '#262a31', color: '#b9cbb9', border: '1px solid rgba(59,75,61,0.4)' }}>
              REVIEW IN VIDEO
            </button>
          </div>

          <BentoCard title="AI OFFSIDE ANALYSIS" icon="architecture" glowColor={isOffside ? 'none' : 'cyan'}>
             <div className="space-y-3 mt-2 font-mono text-sm">
                <div className="flex justify-between text-[#b9cbb9]"><span>AI Assessment</span><span style={{ color: isOffside ? '#ffb4ab' : '#00daf3' }}>{statusLabel}</span></div>
                <div className="flex justify-between text-[#b9cbb9]"><span>Evidence</span><span className="text-[#dfe2eb]">{candidate?.evidence || 'Waiting'}</span></div>
             </div>
          </BentoCard>

          <BentoCard title="Ball Contact" icon="sports_soccer">
             <div className="space-y-3 mt-2">
               <div className="flex justify-between items-center text-sm">
                 <span className="text-[#849585]">Frame ID</span>
                 <span className="font-mono text-[#dfe2eb]">#{frameId}</span>
               </div>
               <div className="flex justify-between items-center text-sm">
                 <span className="text-[#849585]">Timestamp</span>
                 <span className="font-mono text-[#dfe2eb]">{timestamp.toFixed(2)}s</span>
               </div>
               <div className="flex justify-between items-center text-sm">
                 <span className="text-[#849585]">State</span>
                 <span className="font-mono text-[#00daf3]">{candidate?.ball_contact?.state || 'Unknown'}</span>
               </div>
               <div className="flex justify-between items-center text-sm">
                 <span className="text-[#849585]">Confidence</span>
                 <span className="font-mono text-[#dfe2eb]">{candidate?.ball_contact?.confidence ? `${Math.round(candidate.ball_contact.confidence * 100)}%` : '0%'}</span>
               </div>
             </div>
          </BentoCard>
          
          <BentoCard title="Offside Geometry" icon="straighten">
             <div className="space-y-3 mt-2">
               <div className="flex justify-between items-center text-sm">
                 <span className="text-[#849585]">Attacking Dir (A)</span>
                 <span className="font-mono text-[#dfe2eb]">{candidate?.team_a_attacking_dir || 'unknown'}</span>
               </div>
               <div className="flex justify-between items-center text-sm">
                 <span className="text-[#849585]">Def Line (vs A)</span>
                 <span className="font-mono text-[#dfe2eb]">{candidate?.offside_line_against_a?.status === 'available' ? `${candidate.offside_line_against_a.x.toFixed(1)}m (Player #${candidate.offside_line_against_a.defender_id})` : 'unavailable'}</span>
               </div>
               <div className="flex justify-between items-center text-sm">
                 <span className="text-[#849585]">Attacking Dir (B)</span>
                 <span className="font-mono text-[#dfe2eb]">{candidate?.team_b_attacking_dir || 'unknown'}</span>
               </div>
               <div className="flex justify-between items-center text-sm">
                 <span className="text-[#849585]">Def Line (vs B)</span>
                 <span className="font-mono text-[#dfe2eb]">{candidate?.offside_line_against_b?.status === 'available' ? `${candidate.offside_line_against_b.x.toFixed(1)}m (Player #${candidate.offside_line_against_b.defender_id})` : 'unavailable'}</span>
               </div>
             </div>
          </BentoCard>

        </div>
      </div>
    </AppShell>
  );
}
