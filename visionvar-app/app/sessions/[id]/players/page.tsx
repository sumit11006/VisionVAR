import AppShell from '@/components/layout/AppShell';
import { mockPlayers } from '@/lib/mockData/players';
import StatusBadge from '@/components/ui/StatusBadge';

export default function PlayerAnalyticsPage() {
  return (
    <AppShell fullHeight>
      <div className="flex-1 flex flex-col p-4 gap-4 overflow-hidden relative bg-[#0a0e14]">
        
        {/* Top Header */}
        <div className="flex items-center justify-between pb-4" style={{ borderBottom: '1px solid rgba(59,75,61,0.4)' }}>
           <div>
             <h1 className="text-headline-md font-headline-md text-[#f1ffef]">Biometric &amp; Kinematic Tracking</h1>
             <p className="text-body-sm font-body-sm text-[#849585] mt-1">Real-time skeletal node analysis based on DeepLab + Optical Flow</p>
           </div>
           <div className="flex items-center gap-4">
             <div className="flex flex-col items-end">
               <span className="text-label-sm font-label-sm text-[#849585]">ACTIVE TRACKS</span>
               <span className="text-headline-sm font-headline-sm text-[#00daf3]">22 / 22</span>
             </div>
             <StatusBadge label="SKELETAL LOCK ACTIVE" color="emerald" ping />
           </div>
        </div>

        {/* Player Data Grid */}
        <div className="flex-1 overflow-y-auto pr-2">
          <table className="w-full text-left border-collapse">
            <thead className="sticky top-0 bg-[#0a0e14] z-10 text-label-sm font-label-sm text-[#849585]">
              <tr>
                <th className="py-3 px-4 font-normal" style={{ borderBottom: '1px solid rgba(59,75,61,0.5)' }}>Player</th>
                <th className="py-3 px-4 font-normal" style={{ borderBottom: '1px solid rgba(59,75,61,0.5)' }}>Role</th>
                <th className="py-3 px-4 font-normal text-right" style={{ borderBottom: '1px solid rgba(59,75,61,0.5)' }}>Distance (km)</th>
                <th className="py-3 px-4 font-normal text-right" style={{ borderBottom: '1px solid rgba(59,75,61,0.5)' }}>Top Speed</th>
                <th className="py-3 px-4 font-normal text-right" style={{ borderBottom: '1px solid rgba(59,75,61,0.5)' }}>Avg Vel</th>
                <th className="py-3 px-4 font-normal text-center" style={{ borderBottom: '1px solid rgba(59,75,61,0.5)' }}>Sprints</th>
                <th className="py-3 px-4 font-normal text-center" style={{ borderBottom: '1px solid rgba(59,75,61,0.5)' }}>AI Track Conf</th>
                <th className="py-3 px-4 font-normal text-center" style={{ borderBottom: '1px solid rgba(59,75,61,0.5)' }}>Status</th>
              </tr>
            </thead>
            <tbody>
              {mockPlayers.map(player => (
                <tr 
                  key={player.id} 
                  className="hover:bg-[rgba(28,32,38,0.5)] transition-colors group cursor-pointer"
                  style={{ borderBottom: '1px solid rgba(59,75,61,0.2)' }}
                >
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs" style={{ background: '#181c22', border: '1px solid rgba(59,75,61,0.4)', color: player.team.includes('City') ? '#00daf3' : '#dfe2eb' }}>
                        {player.jersey}
                      </div>
                      <div>
                        <div className="font-bold text-[#f1ffef]">{player.name}</div>
                        <div className="text-[10px] text-[#849585]">{player.team} · {player.nationality}</div>
                      </div>
                    </div>
                  </td>
                  <td className="py-3 px-4 text-label-sm font-label-sm text-[#b9cbb9]">{player.role}</td>
                  <td className="py-3 px-4 text-right font-mono text-sm text-[#dfe2eb]">{player.stats.distanceKm.toFixed(2)}</td>
                  <td className="py-3 px-4 text-right font-mono text-sm">
                    <span className={player.stats.topSpeedKph > 35 ? "text-[#00daf3] font-bold" : "text-[#dfe2eb]"}>
                      {player.stats.topSpeedKph.toFixed(1)} km/h
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right font-mono text-sm text-[#b9cbb9]">{player.stats.avgVelocityKph.toFixed(1)}</td>
                  <td className="py-3 px-4 text-center font-mono text-sm text-[#dfe2eb]">{player.stats.sprints}</td>
                  <td className="py-3 px-4 text-center">
                    <div className="inline-flex items-center gap-2">
                      <span className="font-mono text-sm" style={{ color: player.aiConfidence > 98 ? '#00e479' : '#f59e0b' }}>
                        {player.aiConfidence.toFixed(1)}%
                      </span>
                    </div>
                  </td>
                  <td className="py-3 px-4 text-center">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold" style={{ background: 'rgba(0,228,121,0.1)', color: '#00e479', border: '1px solid rgba(0,228,121,0.3)' }}>
                      {player.skeletalLockStatus}
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
