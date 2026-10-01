'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import AppShell from '@/components/layout/AppShell';
import EventCard from '@/components/events/EventCard';
import ScrubberTrack from '@/components/controls/ScrubberTrack';
import TransportControls from '@/components/controls/TransportControls';
import { mockEvents } from '@/lib/mockData/events';
import { fetchMatchEvents } from '@/lib/api';
import type { MatchEvent } from '@/types';

export default function TimelinePage() {
  const params = useParams();
  const matchId = (params?.id as string) || 'UCL-2024-MCI-RMA-F';
  const [events, setEvents] = useState<MatchEvent[]>(mockEvents);
  const activeEventId = 'EVT-010';

  useEffect(() => {
    // 1. Fetch historical events from SQLite
    fetchMatchEvents(matchId)
      .then((data) => {
        if (data && data.length > 0) {
          setEvents(data);
        }
      })
      .catch(() => {
        // Fallback to mockEvents if failed
      });
  }, [matchId]);

  useEffect(() => {
    // 2. Connect WebSocket to stream live AI events (Phase 7A)
    const sessionId = (params?.id as string) || 'default';
    if (sessionId) {
      const ws = new WebSocket(`ws://localhost:8000/ws/analysis/${sessionId}`);
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'event_detected' && data.event) {
            setEvents(prev => {
              // Deduplicate if already exists (sometimes REST returns it just before WS does)
              if (prev.find(e => e.id === data.event.id)) return prev;
              
              const newEvent: MatchEvent = {
                id: data.event.id || data.event.id,
                minute: Math.floor(data.event.timestamp / 60) || 0,
                second: Math.floor(data.event.timestamp % 60) || 0,
                frameId: data.event.frame || 0,
                timecode: '00:00:00:00',
                type: data.event.event_type as EventType,
                team: data.event.team || 'unknown',
                player: data.event.player,
                status: data.event.status,
                confidence: data.event.confidence,
                metadata_json: data.event.metadata ? JSON.stringify(data.event.metadata, null, 2) : undefined,
                aiVerdict: data.event.status,
              };
              
              // Add and sort by time
              return [...prev, newEvent].sort((a, b) => 
                (a.minute * 60 + a.second) - (b.minute * 60 + b.second)
              );
            });
          }
        } catch (e) {
          // ignore parsing error
        }
      };

      return () => ws.close();
    }
  }, [params?.id]);

  return (
    <AppShell fullHeight>
      <div className="flex-1 flex flex-col p-4 gap-4 overflow-hidden relative">

        {/* Top: Video preview (small) and Timeline scrubber (large) */}
        <div className="h-64 flex gap-4">
           {/* Preview Video */}
           <div
             className="w-96 rounded-lg overflow-hidden relative"
             style={{
               background: 'url(https://images.unsplash.com/photo-1518605368461-1e1e11407559?q=80&w=800&auto=format&fit=crop) center/cover',
               border: '1px solid rgba(59,75,61,0.5)'
             }}
           >
             <div className="absolute top-2 right-2 px-1.5 py-0.5 rounded text-[9px] font-mono font-bold tracking-widest text-[#f1ffef]" style={{ background: 'rgba(10,14,20,0.8)' }}>
               CAM-07 TACTICAL
             </div>
             <div className="absolute inset-0 flex items-center justify-center">
                <span className="material-symbols-outlined text-[48px] text-[#00e479] opacity-50 drop-shadow-md">play_circle</span>
             </div>
           </div>

           {/* Timeline Graph */}
           <div className="flex-1 rounded-lg p-4 flex flex-col justify-between" style={{ background: '#181c22', border: '1px solid rgba(59,75,61,0.4)' }}>
             <div className="flex justify-between items-center text-label-sm font-label-sm text-[#849585] mb-2">
               <span>MATCH INCIDENT TIMELINE</span>
               <span>TOTAL EVENTS: {events.length}</span>
             </div>
             
             {/* Multi-track mockup */}
             <div className="flex-1 flex flex-col justify-center gap-4 relative">
                {/* Horizontal tracks */}
                <div className="absolute inset-0 flex flex-col justify-around pointer-events-none opacity-20">
                   <div className="w-full h-px bg-[#3b4b3d]" />
                   <div className="w-full h-px bg-[#3b4b3d]" />
                   <div className="w-full h-px bg-[#3b4b3d]" />
                </div>
                <ScrubberTrack initialValue={4044} />
             </div>
             
             <TransportControls scrubberSeconds={4044} />
           </div>
        </div>

        {/* Bottom: Event List */}
        <div className="flex-1 rounded-lg overflow-hidden flex flex-col" style={{ background: '#0a0e14', border: '1px solid rgba(59,75,61,0.4)' }}>
           <div className="p-3 border-b flex justify-between items-center backdrop-blur-md" style={{ borderColor: 'rgba(59,75,61,0.3)', background: 'rgba(28,32,38,0.8)' }}>
             <h2 className="text-headline-sm font-headline-sm text-[#f1ffef]">Detected Events Log</h2>
             <div className="flex gap-2">
               <input 
                 type="text" 
                 placeholder="Search events, players..." 
                 className="px-3 py-1 rounded text-label-sm font-label-sm text-[#dfe2eb] outline-none"
                 style={{ background: '#181c22', border: '1px solid rgba(59,75,61,0.5)' }}
                 disabled
               />
               <button className="px-3 py-1 rounded text-label-sm font-label-sm flex items-center gap-1.5" style={{ background: '#262a31', color: '#b9cbb9', border: '1px solid rgba(59,75,61,0.5)' }}>
                 <span className="material-symbols-outlined text-[14px]">filter_list</span>
                 Filter
               </button>
             </div>
           </div>
           
           <div className="flex-1 overflow-y-auto p-4 space-y-3">
             {events.map(event => (
               <EventCard key={event.id} event={event} isActive={event.id === activeEventId} />
             ))}
           </div>
        </div>

      </div>
    </AppShell>
  );
}
