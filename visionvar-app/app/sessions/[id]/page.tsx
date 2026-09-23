'use client';

import { useState, useEffect, useRef } from 'react';
import { useParams } from 'next/navigation';
import AppShell from '@/components/layout/AppShell';
import TelemetryChip from '@/components/ui/TelemetryChip';
import CameraAngleSwitcher from '@/components/controls/CameraAngleSwitcher';
import LayerToggles from '@/components/controls/LayerToggles';
import ScrubberTrack from '@/components/controls/ScrubberTrack';
import { mockCameras } from '@/lib/mockData/match';
import PitchSVGRadar from '@/components/radar/PitchSVGRadar';
import StatusBadge from '@/components/ui/StatusBadge';
import {
  fetchSession,
  connectAnalysisWebSocket,
  startDetection,
  TrackedItem,
  FrameTrackingMessage,
  ProcessingStatusMessage,
} from '@/lib/api';
import type { VideoMetadata } from '@/types';

export default function LiveWorkspacePage() {
  const params = useParams();
  const sessionId = (params?.id as string) || 'UCL-2024-MCI-RMA-F';

  // Video stream & metadata state
  const [sessionData, setSessionData] = useState<MatchSession | null>(null);
  const [videoMeta, setVideoMeta] = useState<VideoMetadata | null>(null);
  const [duration, setDuration] = useState<number>(12.0);
  const [fps, setFps] = useState<number>(30.0);
  const [totalFrames, setTotalFrames] = useState<number>(0);
  const [resolution, setResolution] = useState<string>('Pending analysis');
  const [videoWidth, setVideoWidth] = useState<number>(1280);
  const [videoHeight, setVideoHeight] = useState<number>(720);

  // Playback & Frame state
  const [currentFrame, setCurrentFrame] = useState<number>(0);
  const [currentSeconds, setCurrentSeconds] = useState<number>(0.0);

  // Live real tracking state
  const [trackedItems, setTrackedItems] = useState<TrackedItem[]>([]);
  const [inferenceMs, setInferenceMs] = useState<number | null>(null);
  const [trackingMs, setTrackingMs] = useState<number | null>(null);
  const [detectionStatus, setDetectionStatus] = useState<string>('IDLE');
  const [progress, setProgress] = useState<number>(0);
  const [isLiveWsConnected, setIsLiveWsConnected] = useState<boolean>(false);
  const wsRef = useRef<WebSocket | null>(null);
  const videoRef = useRef<HTMLVideoElement | null>(null);

  // Load session & video metadata from backend
  useEffect(() => {
    let isMounted = true;
    fetchSession(sessionId)
      .then((session) => {
        if (!isMounted) return;
        setSessionData(session);
        if (session.video_metadata) {
          const meta = session.video_metadata;
          setVideoMeta(meta);
          if (meta.duration_seconds && meta.duration_seconds > 0) {
            setDuration(meta.duration_seconds);
          }
          if (meta.fps && meta.fps > 0) {
            setFps(meta.fps);
          }
          if (meta.total_frames && meta.total_frames > 0) {
            setTotalFrames(meta.total_frames);
          }
          if (meta.resolution) {
            setResolution(meta.resolution);
          }
          if (meta.width > 0) setVideoWidth(meta.width);
          if (meta.height > 0) setVideoHeight(meta.height);
        } else {
          setResolution('No Video Attached');
        }
      })
      .catch(() => {
        // Fallback gracefully
      });

    return () => {
      isMounted = false;
    };
  }, [sessionId]);

  // Connect to live analysis WebSocket
  useEffect(() => {
    const ws = connectAnalysisWebSocket(
      sessionId,
      (data) => {
        const type = data.type as string;
        if (type === 'frame_tracking') {
          const frameMsg = data as unknown as FrameTrackingMessage;
          setCurrentFrame(frameMsg.frame);
          setTrackedItems(frameMsg.tracked_items || []);
          if (frameMsg.inference_time_ms) {
            setInferenceMs(frameMsg.inference_time_ms);
          }
          if (frameMsg.tracking_time_ms) {
            setTrackingMs(frameMsg.tracking_time_ms);
          }
          if (frameMsg.total_frames) {
            setTotalFrames(frameMsg.total_frames);
          }
          if (frameMsg.fps) {
            setFps(frameMsg.fps);
          }
          if (frameMsg.duration_seconds) {
            setDuration(frameMsg.duration_seconds);
          }
          if (frameMsg.width) setVideoWidth(frameMsg.width);
          if (frameMsg.height) setVideoHeight(frameMsg.height);

          const secs = frameMsg.timestamp !== undefined
            ? frameMsg.timestamp
            : (frameMsg.frame / (frameMsg.fps || fps || 30.0));
          setCurrentSeconds(secs);
          if (videoRef.current && !videoRef.current.seeking) {
            videoRef.current.currentTime = secs;
          }
        } else if (type === 'processing_status') {
          const statusMsg = data as unknown as ProcessingStatusMessage;
          setDetectionStatus(statusMsg.status.toUpperCase());
          setProgress(statusMsg.progress);
          if (statusMsg.total_frames) setTotalFrames(statusMsg.total_frames);
          if (statusMsg.fps) setFps(statusMsg.fps);
          if (statusMsg.duration_seconds) setDuration(statusMsg.duration_seconds);
          if (statusMsg.resolution) setResolution(statusMsg.resolution);
          if (statusMsg.width) setVideoWidth(statusMsg.width);
          if (statusMsg.height) setVideoHeight(statusMsg.height);
        }
      },
      () => setIsLiveWsConnected(true),
      () => setIsLiveWsConnected(false)
    );

    wsRef.current = ws;
    return () => {
      ws.close();
    };
  }, [sessionId, fps]);

  const handleStartRealDetection = async () => {
    try {
      setDetectionStatus('PROCESSING');
      setProgress(5);
      const res = await startDetection(sessionId, { frame_skip: 4, confidence_threshold: 0.25 });
      if (res.total_frames) setTotalFrames(res.total_frames);
      if (res.fps) setFps(res.fps);
      if (res.duration_seconds) setDuration(res.duration_seconds);
    } catch {
      setDetectionStatus('ERROR');
    }
  };

  // Derive live telemetry values from real tracking
  const activePlayers = trackedItems.filter((d) => d.class === 'player');
  const ballItem = trackedItems.find((d) => d.class === 'ball');
  const avgConfidence = trackedItems.length > 0
    ? (trackedItems.reduce((acc, d) => acc + d.confidence, 0) / trackedItems.length) * 100
    : null;

  // Real REC timecode derived strictly from actual video seconds
  const mins = Math.floor(currentSeconds / 60);
  const secs = Math.floor(currentSeconds % 60);
  const millis = Math.floor((currentSeconds % 1) * 1000);
  const recTimecode = `00:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}.${millis.toString().padStart(3, '0')}`;

  const videoStreamUrl = videoMeta?.video_id
    ? `http://localhost:8000/api/videos/${videoMeta.video_id}/file`
    : null;

  return (
    <AppShell fullHeight>
      <div className="flex-1 flex flex-col p-4 gap-4 overflow-hidden relative">
        {/* Glow overlay */}
        <div
          className="absolute top-1/4 left-1/4 w-[40vw] h-[40vh] rounded-full pointer-events-none mix-blend-screen opacity-10"
          style={{ background: '#00e479', filter: 'blur(100px)' }}
        />

        {/* Video Area */}
        <div
          className="relative flex-1 rounded-lg overflow-hidden flex flex-col justify-end bg-[#0a0e14]"
          style={{
            border: '1px solid rgba(0,228,121,0.5)',
            boxShadow: '0 0 24px rgba(0,255,136,0.1)',
          }}
        >
          {/* HTML5 Video Element if available, otherwise stylized pitch backdrop */}
          {videoStreamUrl ? (
            <video
              ref={videoRef}
              src={videoStreamUrl}
              className="absolute inset-0 w-full h-full object-contain pointer-events-none"
              muted
              playsInline
            />
          ) : (
            <div
              className="absolute inset-0"
              style={{
                background:
                  'url(https://images.unsplash.com/photo-1518605368461-1e1e11407559?q=80&w=2070&auto=format&fit=crop) center/cover',
                opacity: 0.7,
              }}
            />
          )}

          {/* Top-left match identity badge */}
          <div className="absolute top-4 left-4 flex items-center gap-2 z-10">
            <div
              className="px-2.5 py-1 rounded backdrop-blur-md flex items-center gap-2 text-label-sm font-label-sm font-bold"
              style={{
                background: 'rgba(10,14,20,0.85)',
                border: '1px solid rgba(59,75,61,0.5)',
                color: '#f1ffef',
              }}
            >
              <span className="material-symbols-outlined text-[15px] text-[#00e479]">sports_soccer</span>
              <span>{sessionData ? `${sessionData.homeTeam} vs ${sessionData.awayTeam}` : sessionId}</span>
              {sessionData?.competition && (
                <span className="text-[#849585] font-normal hidden sm:inline">· {sessionData.competition}</span>
              )}
            </div>
          </div>

          {/* Top-right overlay badges */}
          <div className="absolute top-4 right-4 flex flex-col items-end gap-2 z-10">
            <div className="flex items-center gap-2">
              <span
                className="px-2 py-1 rounded text-label-sm font-label-sm font-bold tracking-wider"
                style={{
                  background: 'rgba(10,14,20,0.85)',
                  border: '1px solid rgba(0,218,243,0.5)',
                  color: '#00daf3',
                }}
              >
                {detectionStatus === 'PROCESSING'
                  ? `YOLO RUNNING (${progress}%)`
                  : resolution !== 'Pending analysis'
                  ? `${resolution} • ${fps.toFixed(1)} FPS`
                  : 'RAW VIDEO FEED'}
              </span>
              <StatusBadge
                label={isLiveWsConnected ? 'LIVE FEED' : 'STANDBY'}
                color={isLiveWsConnected ? 'emerald' : 'amber'}
                ping
                pulse
              />
            </div>
            <div
              className="px-2 py-0.5 rounded text-[10px] font-mono tracking-widest text-[#f1ffef]"
              style={{ background: 'rgba(10,14,20,0.85)', border: '1px solid rgba(59,75,61,0.4)' }}
            >
              REC: {recTimecode}
            </div>
          </div>

          {/* Real YOLO Bounding Box Overlays */}
          <div className="absolute inset-0 pointer-events-none overflow-hidden">
            {trackedItems.length > 0 ? (
              // Map real YOLO tracking boxes normalized across container
              trackedItems.map((det, idx) => {
                const isBall = det.class === 'ball';
                const w = videoWidth > 0 ? videoWidth : 1280;
                const h = videoHeight > 0 ? videoHeight : 720;
                const left = (det.bbox.x1 / w) * 100;
                const top = (det.bbox.y1 / h) * 100;
                const boxW = ((det.bbox.x2 - det.bbox.x1) / w) * 100;
                const boxH = ((det.bbox.y2 - det.bbox.y1) / h) * 100;
                const confPct = Math.round(det.confidence * 100);

                return (
                  <div
                    key={idx}
                    className="absolute transition-all duration-75"
                    style={{
                      left: `${left}%`,
                      top: `${top}%`,
                      width: `${Math.max(2, boxW)}%`,
                      height: `${Math.max(2, boxH)}%`,
                      border: isBall ? '2px solid #ffd700' : '2px solid #00e479',
                      boxShadow: isBall ? '0 0 12px rgba(255,215,0,0.7)' : '0 0 10px rgba(0,228,121,0.5)',
                      borderRadius: isBall ? '9999px' : '2px',
                    }}
                  >
                    <div
                      className="absolute -top-5 left-0 text-[9px] px-1 font-mono font-bold whitespace-nowrap"
                      style={{
                        background: isBall ? '#ffd700' : '#00e479',
                        color: '#0a0e14',
                      }}
                    >
                      {isBall ? `BALL [${confPct}%]` : `#${det.track_id} PLAYER [${confPct}%]`}
                    </div>
                  </div>
                );
              })
            ) : !videoMeta ? (
              // Helpful indicator when no video is attached to this session
              <div className="absolute inset-0 flex items-center justify-center pointer-events-auto">
                <div
                  className="flex flex-col items-center gap-3 px-6 py-5 rounded-xl backdrop-blur-md max-w-md text-center"
                  style={{
                    background: 'rgba(10,14,20,0.88)',
                    border: '1px solid rgba(59,75,61,0.6)',
                    boxShadow: '0 0 24px rgba(0,0,0,0.6)',
                  }}
                >
                  <span className="material-symbols-outlined text-[32px] text-[#00daf3]">video_file</span>
                  <div className="text-headline-sm font-headline-sm font-bold text-[#f1ffef]">
                    No Video Attached
                  </div>
                  <p className="text-body-sm font-body-sm text-[#849585]">
                    This session doesn&apos;t have an uploaded video linked to it yet. Upload a match clip to run real YOLO intelligence.
                  </p>
                  <a
                    href="/sessions"
                    className="mt-1 px-4 py-2 rounded text-label-sm font-label-sm font-bold uppercase tracking-wider text-[#0a0e14] bg-[#00e479] hover:brightness-110 transition-all flex items-center gap-1.5"
                  >
                    <span className="material-symbols-outlined text-[16px]">cloud_upload</span>
                    Upload Match Video →
                  </a>
                </div>
              </div>
            ) : detectionStatus === 'IDLE' ? (
              // Clean HUD standby indicator without fabricated boxes
              <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                <div
                  className="flex flex-col items-center gap-2 px-4 py-3 rounded backdrop-blur-md"
                  style={{
                    background: 'rgba(10,14,20,0.8)',
                    border: '1px solid rgba(0,228,121,0.4)',
                    boxShadow: '0 0 20px rgba(0,228,121,0.1)',
                  }}
                >
                  <div className="flex items-center gap-2 text-label-sm font-label-sm tracking-wider text-[#00e479] font-bold">
                    <span className="w-2 h-2 rounded-full bg-[#00e479] animate-pulse" />
                    OPENCV VIDEO LOADED ({duration.toFixed(1)}s • {totalFrames || Math.round(duration * fps)} FRAMES)
                  </div>
                  <div className="text-[11px] font-mono text-[#849585]">
                    Click &quot;Run YOLO Detect&quot; to stream real detections
                  </div>
                </div>
              </div>
            ) : null}
          </div>

          {/* Bottom HUD bar within video */}
          <div
            className="w-full p-3 backdrop-blur-md flex flex-col gap-3 z-10"
            style={{
              background: 'linear-gradient(to top, rgba(10,14,20,0.95), rgba(10,14,20,0.6))',
              borderTop: '1px solid rgba(59,75,61,0.5)',
            }}
          >
            {/* Scrubber scaled to actual video duration */}
            <div className="w-full">
              <ScrubberTrack
                currentSeconds={currentSeconds}
                durationSeconds={duration}
                fps={fps}
                totalFrames={totalFrames}
                onValueChange={(sec, frame) => {
                  setCurrentSeconds(sec);
                  if (frame !== undefined) setCurrentFrame(frame);
                  if (videoRef.current) {
                    videoRef.current.currentTime = sec;
                  }
                }}
              />
            </div>

            {/* Controls */}
            <div className="flex items-center justify-between">
              <CameraAngleSwitcher cameras={mockCameras} initialCamera="main" />
              <LayerToggles />
            </div>
          </div>
        </div>

        {/* Bottom Drawer (Telemetry Grid) */}
        <div
          className="h-48 rounded-lg p-3 grid grid-cols-12 gap-4"
          style={{ background: '#181c22', border: '1px solid rgba(59,75,61,0.4)' }}
        >
          {/* Radar */}
          <div className="col-span-3 h-full flex flex-col gap-2">
            <div className="text-label-sm font-label-sm text-[#849585] uppercase tracking-wider flex items-center justify-between">
              <span className="flex items-center gap-1.5">
                <span className="material-symbols-outlined text-[14px]">radar</span>
                Pitch Projection
              </span>
              <span className="text-[9px] font-mono text-[#849585]">2D RADAR</span>
            </div>
            <div className="flex-1 relative">
              <PitchSVGRadar teamADots={[]} teamBDots={[]} height="h-full" />
              <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                <span className="px-2 py-1 rounded text-[9px] font-mono bg-[rgba(10,14,20,0.75)] text-[#849585] border border-[rgba(59,75,61,0.4)]">
                  Radar mapping: Pending tracking
                </span>
              </div>
            </div>
          </div>

          {/* Telemetry Stats - Strict calculation policy */}
          <div className="col-span-9 grid grid-cols-5 gap-3 h-full">
            <div className="flex flex-col gap-3 border-r pr-3" style={{ borderColor: 'rgba(59,75,61,0.3)' }}>
              <TelemetryChip label="Inference Engine" value="YOLOv8n Neural Core" />
              <TelemetryChip
                label="AI Confidence"
                value={avgConfidence !== null ? `${avgConfidence.toFixed(1)}%` : 'Pending analysis'}
                valueColor={avgConfidence !== null ? '#00e479' : '#849585'}
              />
            </div>
            <div className="flex flex-col gap-3 border-r pr-3" style={{ borderColor: 'rgba(59,75,61,0.3)' }}>
              <TelemetryChip
                label="Tracked Objects"
                value={
                  detectionStatus === 'PROCESSING' || trackedItems.length > 0
                    ? `${activePlayers.length} P | ${ballItem ? 1 : 0} B`
                    : 'Pending analysis'
                }
              />
              <TelemetryChip
                label="Current Frame"
                value={
                  totalFrames > 0
                    ? `#${currentFrame.toLocaleString()} / ${totalFrames.toLocaleString()}`
                    : `#${currentFrame.toLocaleString()}`
                }
                valueColor="#00daf3"
              />
            </div>
            <div className="flex flex-col gap-3 border-r pr-3" style={{ borderColor: 'rgba(59,75,61,0.3)' }}>
              <TelemetryChip
                label="Inference Latency"
                value={inferenceMs !== null ? `${inferenceMs.toFixed(1)}ms` : 'Standby'}
                valueColor={inferenceMs !== null ? '#00daf3' : '#849585'}
              />
              <TelemetryChip label="Optical Calib" value="Not available" />
            </div>
            <div className="flex flex-col gap-3 border-r pr-3" style={{ borderColor: 'rgba(59,75,61,0.3)' }}>
              <TelemetryChip
                label="Ball Visibility"
                value={
                  detectionStatus === 'PROCESSING' || trackedItems.length > 0
                    ? ballItem
                      ? `LOCKED (${Math.round(ballItem.confidence * 100)}%)`
                      : 'NOT DETECTED'
                    : 'Pending analysis'
                }
                valueColor={ballItem ? '#00e479' : '#f59e0b'}
              />
              <TelemetryChip label="Ball Velocity" value="Not available" />
            </div>
            <div className="flex flex-col gap-3 justify-center h-full">
              <button
                onClick={handleStartRealDetection}
                disabled={detectionStatus === 'PROCESSING'}
                className="w-full py-3 rounded text-label-md font-label-md font-bold uppercase tracking-wider hover:brightness-110 active:scale-95 transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed"
                style={{
                  background: detectionStatus === 'PROCESSING' ? '#f59e0b' : '#00e479',
                  color: '#0a0e14',
                  boxShadow: '0 0 16px rgba(0,228,121,0.3)',
                }}
              >
                <span className="material-symbols-outlined text-[18px]">
                  {detectionStatus === 'PROCESSING' ? 'autorenew' : 'smart_toy'}
                </span>
                {detectionStatus === 'PROCESSING' ? 'Processing...' : 'Run YOLO Detect'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}

