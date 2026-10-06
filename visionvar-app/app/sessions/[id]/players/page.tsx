'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import AppShell from '@/components/layout/AppShell';
import { fetchMatchAnalytics } from '@/lib/api';
import StatusBadge from '@/components/ui/StatusBadge';

export default function PlayerAnalyticsPage() {
  const params = useParams();
  const matchId = (params?.id as string) || 'UCL-2024-MCI-RMA-F';
  const [players, setPlayers] = useState<any[]>([]);

  useEffect(() => {
    fetchMatchAnalytics(matchId)
      .then(data => {
        if (data.players) {
          // Sort by team, then ID
          setPlayers(data.players.sort((a: any, b: any) => {
            if (a.team !== b.team) return a.team.localeCompare(b.team);
            return parseInt(a.player_id) - parseInt(b.player_id);
          }));
        }
      })
      .catch(console.error);
  }, [matchId]);
  return (
    <AppShell fullHeight>
      <div className="flex-1 flex flex-col p-4 gap-4 overflow-hidden relative bg-[#0a0e14]">
        
        {/* Top Header */}
        <div className="flex items-center justify-between pb-4" style={{ borderBottom: '1px solid rgba(59,75,61,0.4)' }}>
           <div>
             <h1 className="text-headline-md font-headline-md text-[#f1ffef]">Tracking &amp; Kinematic Analytics</h1>
             <p className="text-body-sm font-body-sm text-[#849585] mt-1">Real-time object tracking based on YOLOv8 + ByteTrack</p>
           </div>
           <div className="flex items-center gap-4">
             <div className="flex flex-col items-end">
               <span className="text-label-sm font-label-sm text-[#849585]">ACTIVE TRACKS</span>
               <span className="text-headline-sm font-headline-sm text-[#00daf3]">{players.length}</span>
             </div>
             <StatusBadge label="SKELETAL LOCK ACTIVE" color="emerald" ping />
           </div>
        </div>

        {/* Player Data Grid */}
        <div className="flex-1 overflow-y-auto pr-2">
          <table className="w-full text-left border-collapse">
            <thead className="sticky top-0 bg-[#0a0e14] z-10 text-label-sm font-label-sm text-[#849585]">
              <tr>
                <th className="py-3 px-4 font-normal" style={{ borderBottom: '1px solid rgba(59,75,61,0.5)' }}>Track ID</th>
                <th className="py-3 px-4 font-normal" style={{ borderBottom: '1px solid rgba(59,75,61,0.5)' }}>Role</th>
                <th className="py-3 px-4 font-normal text-right" style={{ borderBottom: '1px solid rgba(59,75,61,0.5)' }}>Distance (km)</th>
                <th className="py-3 px-4 font-normal text-right" style={{ borderBottom: '1px solid rgba(59,75,61,0.5)' }}>Top Speed</th>
                <th className="py-3 px-4 font-normal text-right" style={{ borderBottom: '1px solid rgba(59,75,61,0.5)' }}>Avg Vel (km/h)</th>
                <th className="py-3 px-4 font-normal text-center" style={{ borderBottom: '1px solid rgba(59,75,61,0.5)' }}>Touches</th>
                <th className="py-3 px-4 font-normal text-center" style={{ borderBottom: '1px solid rgba(59,75,61,0.5)' }}>Samples</th>
                <th className="py-3 px-4 font-normal text-center" style={{ borderBottom: '1px solid rgba(59,75,61,0.5)' }}>Status</th>
              </tr>
            </thead>
            <tbody>
              {players.length === 0 && (
                <tr><td colSpan={8} className="text-center py-4 text-[#849585]">Loading real analytics data...</td></tr>
              )}
              {players.map(player => (
                <tr 
                  key={player.player_id} 
                  className="hover:bg-[rgba(28,32,38,0.5)] transition-colors group cursor-pointer"
                  style={{ borderBottom: '1px solid rgba(59,75,61,0.2)' }}
                >
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs" style={{ background: '#181c22', border: '1px solid rgba(59,75,61,0.4)', color: player.team !== 'unknown' ? '#00daf3' : '#dfe2eb' }}>
                        {player.player_id}
                      </div>
                      <div>
                        <div className="font-bold text-[#f1ffef]">Track ID {player.player_id}</div>
                        <div className="text-[10px] text-[#849585]">{player.team}</div>
                      </div>
                    </div>
                  </td>
                  <td className="py-3 px-4 text-label-sm font-label-sm text-[#b9cbb9]">FLD</td>
                  <td className="py-3 px-4 text-right font-mono text-sm text-[#dfe2eb]">{(player.estimated_distance_m / 1000).toFixed(2)}</td>
                  <td className="py-3 px-4 text-right font-mono text-sm">
                    <span className={player.estimated_max_speed_mps > 8 ? "text-[#00daf3] font-bold" : "text-[#dfe2eb]"}>
                      {((player.estimated_max_speed_mps || 0) * 3.6).toFixed(1)} km/h
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right font-mono text-sm text-[#b9cbb9]">{((player.estimated_avg_speed_mps || 0) * 3.6).toFixed(1)}</td>
                  <td className="py-3 px-4 text-center font-mono text-sm text-[#dfe2eb]">{player.touches}</td>
                  <td className="py-3 px-4 text-center">
                    <div className="inline-flex items-center gap-2">
                      <span className="font-mono text-sm text-[#00e479]">
                        {player.data_quality?.mapped_samples}
                      </span>
                    </div>
                  </td>
                  <td className="py-3 px-4 text-center">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold" style={{ background: 'rgba(0,228,121,0.1)', color: '#00e479', border: '1px solid rgba(0,228,121,0.3)' }}>
                      MAPPED
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

      </div>
    </AppShell>
  );
}
