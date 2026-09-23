'use client';

import { useState, useEffect, useRef } from 'react';
import AppShell from '@/components/layout/AppShell';
import PipelineStageCard from '@/components/pipeline/PipelineStageCard';
import MatchSessionCard from '@/components/pipeline/MatchSessionCard';
import { mockPipelineStages, mockSessions } from '@/lib/mockData/match';
import { fetchSessions, uploadVideo } from '@/lib/api';
import type { MatchSession } from '@/types';

import { useRouter } from 'next/navigation';

const LOG_LINES = [
  { time: '01:07:24.482', text: '[YOLO-v9] Ball centroid locked — Frame #121,418 | Velocity: 86.4 km/h | Trajectory: Forward-arc confirmed', color: '#00e479' },
  { time: '01:07:24.190', text: '[SAOT] Attacker-Defender axis computed: 34.08m vs 34.22m | Delta: +14.2cm | Uncertainty: ±1.8cm', color: '#00daf3' },
  { time: '01:07:23.842', text: '[KALMAN] Player skeleton keypoints re-locked — Mount #19 confidence: 98.8% | Dier #15 confidence: 99.2%', color: '#c0c1ff' },
  { time: '01:07:23.410', text: '[HOMO3D] Pitch homography matrix recalibrated — RMSE: 0.08px | V-points: 12', color: '#b9cbb9' },
  { time: '01:07:22.918', text: '[PIPELINE] Stage 3 (YOLOv9 Ball Tracking) → 88% complete | ETA to Stage 4: ~2.4s', color: '#849585' },
];

export default function SessionsPage() {
  const router = useRouter();
  const [sessions, setSessions] = useState<MatchSession[]>(mockSessions);
  const [uploadStatus, setUploadStatus] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    fetchSessions()
      .then((data) => {
        if (data && data.length > 0) {
          setSessions(data);
        }
      })
      .catch(() => {
        // Fallback gracefully to mockSessions
      });
  }, []);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      setUploadStatus(`Uploading ${file.name}...`);
      const res = await uploadVideo(file);
      setUploadStatus(`Uploaded (${res.duration_seconds || 'clip'}s)! Opening workspace...`);
      // Refresh sessions
      const updated = await fetchSessions().catch(() => null);
      if (updated) setSessions(updated);
      
      // Navigate directly to the dedicated workspace for this uploaded video
      const targetSessionId = res.session_id || `session_${res.video_id}`;
      setTimeout(() => {
        router.push(`/sessions/${targetSessionId}`);
      }, 800);
    } catch (err: unknown) {
      setUploadStatus(`Upload failed: ${err instanceof Error ? err.message : 'Error'}`);
      setTimeout(() => setUploadStatus(null), 4000);
    }
  };
  return (
    <AppShell>
      {/* Ambient glow */}
      <div className="fixed top-20 right-1/4 w-96 h-96 rounded-full pointer-events-none z-0" style={{ background: 'rgba(0,228,121,0.03)', filter: 'blur(80px)' }} />
      <div className="fixed bottom-10 left-1/4 w-80 h-80 rounded-full pointer-events-none z-0" style={{ background: 'rgba(0,218,243,0.03)', filter: 'blur(80px)' }} />
      <div className="hud-grid-pattern fixed inset-0 pointer-events-none opacity-20 z-0" />

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">

        {/* Hero */}
        <section
          className="rounded-xl p-6 lg:p-8 relative overflow-hidden"
          style={{ background: 'rgba(28,32,38,0.6)', border: '1px solid rgba(59,75,61,0.4)', backdropFilter: 'blur(24px)' }}
        >
          {/* Watermark wireframe */}
          <div className="absolute -right-12 -top-16 w-96 h-96 opacity-10 pointer-events-none">
            <div className="w-full h-full rounded-full flex items-center justify-center" style={{ border: '1px solid #00e479' }}>
              <div className="w-2/3 h-2/3 rounded-full flex items-center justify-center" style={{ border: '1px solid #00daf3' }}>
                <div className="w-1/3 h-1/3 rotate-45" style={{ border: '1px solid #00e479' }} />
              </div>
            </div>
          </div>

          <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
            <div className="max-w-2xl">
              <div
                className="inline-flex items-center gap-2 px-2.5 py-1 rounded text-label-sm font-label-sm text-[#00daf3] mb-3"
                style={{ background: 'rgba(59,75,61,0.8)', border: '1px solid rgba(59,75,61,0.6)' }}
              >
                <span className="w-1.5 h-1.5 rounded-full bg-[#00daf3] animate-ping" />
                SUB-MILLIMETER CALIBRATION ENGINE READY
              </div>
              <h1 className="text-headline-lg font-headline-lg text-[#f1ffef] tracking-tight">
                VisionVAR Neural Pitch Intelligence
              </h1>
              <p className="text-body-lg font-body-lg text-[#b9cbb9] mt-2 max-w-xl">
                Next-generation AI football video analysis &amp; automated VAR system. Real-time multi-camera synchronicity, skeletal limb keypoint tracking, and homography 3D pitch spatial reconstruction.
              </p>
            </div>

            {/* Telemetry status cockpit */}
            <div
              className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-3 rounded-lg"
              style={{ background: 'rgba(10,14,20,0.8)', border: '1px solid rgba(59,75,61,0.4)' }}
            >
              {[
                { label: 'TOTAL FRAMES', value: '162,000', sub: '4K 60FPS SYNCD', color: '#f1ffef' },
                { label: 'INFERENCE', value: '14.2ms', sub: 'ZERO LAG', color: '#00e479' },
                { label: 'GPU CLUSTER', value: '74%', sub: '8x H100 NODES', color: '#00daf3' },
                { label: 'PITCH CALIB', value: '±0.08mm', sub: 'GRADE A', color: '#f1ffef' },
              ].map((s, i) => (
                <div key={i} className={i < 3 ? 'border-r pr-3' : ''} style={{ borderColor: 'rgba(59,75,61,0.3)' }}>
                  <span className="text-label-sm font-label-sm text-[#b9cbb9] block">{s.label}</span>
                  <span className="text-label-lg font-label-lg font-bold" style={{ color: s.color }}>{s.value}</span>
                  <span className="text-[10px] text-[#00e479] font-label-sm block">{s.sub}</span>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Upload / Connect actions */}
        <input
          ref={fileInputRef}
          type="file"
          accept=".mp4,.mkv,.mov,.avi,.ts"
          onChange={handleFileUpload}
          className="hidden"
        />
        <section className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[
            {
              icon: 'cloud_upload', iconColor: '#00e479',
              title: 'Upload Match Video',
              desc: 'MP4, MKV, ProRes up to 8K 60FPS broadcast containers',
              badge: uploadStatus || 'LOCAL / S3',
              detail: 'Batch Multi-Angle Auto-Stitching Supported',
              detailIcon: 'tune',
              cta: uploadStatus ? uploadStatus : 'Select Files →',
              ctaColor: '#00e479',
              hoverBorder: '#00e479',
              onClick: () => fileInputRef.current?.click(),
            },
            {
              icon: 'sensors', iconColor: '#00daf3',
              title: 'Connect Live Optical Pitch Feed',
              desc: 'RTSP / SDI direct optical matrix with 12ms target latency',
              badge: 'BROADCAST LINK',
              detail: 'IP: 192.168.10.88:554/live/var-feed-01',
              detailIcon: 'router',
              cta: 'Link Stream →',
              ctaColor: '#00daf3',
              hoverBorder: '#00daf3',
              onClick: undefined,
            },
          ].map((card, i) => (
            <div
              key={i}
              className="group rounded-xl p-5 transition-all duration-200 cursor-pointer overflow-hidden"
              style={{ background: 'rgba(28,32,38,0.5)', border: '1px solid rgba(59,75,61,0.5)' }}
              onMouseEnter={(e) => (e.currentTarget.style.border = `1px solid ${card.hoverBorder}60`)}
              onMouseLeave={(e) => (e.currentTarget.style.border = '1px solid rgba(59,75,61,0.5)')}
              onClick={card.onClick}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3.5">
                  <div
                    className="w-12 h-12 rounded-lg flex items-center justify-center transition-all"
                    style={{ background: '#31353c', border: '1px solid rgba(59,75,61,0.6)', color: card.iconColor }}
                  >
                    <span className="material-symbols-outlined text-[24px]">{card.icon}</span>
                  </div>
                  <div>
                    <div className="text-headline-sm font-headline-sm text-[#f1ffef]">{card.title}</div>
                    <p className="text-body-sm font-body-sm text-[#b9cbb9] mt-0.5">{card.desc}</p>
                  </div>
                </div>
                <span
                  className="px-2 py-0.5 rounded text-label-sm font-label-sm shrink-0"
                  style={{ background: '#0a0e14', border: '1px solid rgba(59,75,61,0.6)', color: card.ctaColor }}
                >
                  {card.badge}
                </span>
              </div>
              <div className="mt-4 pt-3 flex items-center justify-between" style={{ borderTop: '1px solid rgba(59,75,61,0.3)' }}>
                <div className="flex items-center gap-2 text-label-sm font-label-sm text-[#b9cbb9]">
                  <span className="material-symbols-outlined text-[14px]">{card.detailIcon}</span>
                  <span>{card.detail}</span>
                </div>
                <span className="text-label-sm font-label-sm font-semibold flex items-center" style={{ color: card.ctaColor }}>
                  {card.cta}
                </span>
              </div>
            </div>
          ))}
        </section>

        {/* Neural Pipeline */}
        <section
          className="rounded-xl p-5 space-y-4"
          style={{ background: 'rgba(28,32,38,0.7)', border: '1px solid rgba(59,75,61,0.4)', backdropFilter: 'blur(24px)' }}
        >
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div className="flex items-center gap-2.5">
              <span className="w-2.5 h-2.5 rounded-full bg-[#00e479]" style={{ boxShadow: '0 0 8px rgba(0,255,136,0.6)' }} />
              <h2 className="text-headline-sm font-headline-sm text-[#f1ffef]">Neural Inference Pipeline Architecture</h2>
              <span
                className="text-label-sm font-label-sm text-[#b9cbb9] px-2 py-0.5 rounded"
                style={{ background: '#262a31', border: '1px solid rgba(59,75,61,0.4)' }}
              >
                PIPELINE ID: #VAR-ENG-9884
              </span>
            </div>
            <div className="flex items-center gap-4 text-label-sm font-label-sm text-[#b9cbb9]">
              <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-[#00e479]" /> Complete</span>
              <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-[#00daf3] animate-pulse" /> Active (Stage 3)</span>
              <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-[#849585]" /> Pending</span>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-3 pt-2">
            {mockPipelineStages.map(stage => (
              <PipelineStageCard key={stage.stage} stage={stage} />
            ))}
          </div>
        </section>

        {/* Log terminal + Sessions */}
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
          {/* Log terminal */}
          <div
            className="lg:col-span-2 rounded-xl p-4 flex flex-col gap-3"
            style={{ background: '#0a0e14', border: '1px solid rgba(59,75,61,0.4)', fontFamily: 'JetBrains Mono, monospace' }}
          >
            <div className="flex items-center gap-2 pb-2" style={{ borderBottom: '1px solid rgba(59,75,61,0.3)' }}>
              <span className="material-symbols-outlined text-[#00e479] text-[16px]">terminal</span>
              <span className="text-label-md font-label-md font-bold text-[#dfe2eb]">Live Inference Log</span>
              <span className="ml-auto text-label-sm font-label-sm text-[#00daf3] flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-[#00daf3] animate-ping" /> STREAMING
              </span>
            </div>
            <div className="space-y-2 overflow-y-auto max-h-48">
              {LOG_LINES.map((line, i) => (
                <div key={i} className="flex gap-2 text-[10px] leading-relaxed">
                  <span className="text-[#849585] shrink-0 font-mono">{line.time}</span>
                  <span style={{ color: line.color }}>{line.text}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Sessions grid */}
          <div className="lg:col-span-3">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-headline-sm font-headline-sm text-[#f1ffef]">Recent Sessions</h2>
              <span className="text-label-sm font-label-sm text-[#b9cbb9]">PIPELINE ID: #VAR-ENG-9884</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {sessions.map(session => (
                <MatchSessionCard key={session.id} session={session} />
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <footer className="flex items-center justify-between py-4 text-label-sm font-label-sm text-[#849585]" style={{ borderTop: '1px solid rgba(59,75,61,0.3)' }}>
          <span>VisionVAR AI Platform · All analysis is automated and advisory only</span>
          <span className="text-[#b9cbb9]">SERVER: COCKPIT-ID #VAR-ENG-9884</span>
        </footer>
      </div>
    </AppShell>
  );
}
