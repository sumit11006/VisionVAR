import json
from datetime import datetime, timezone
from fastapi import WebSocket, WebSocketDisconnect
from backend.app.websocket.manager import ws_manager


async def analysis_websocket_endpoint(websocket: WebSocket, session_id: str):
    await ws_manager.connect(session_id, websocket)
    try:
        # Send initial handshake message
        await websocket.send_json({
            "type": "connected",
            "session_id": session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": f"Connected to VisionVAR live analysis stream for session '{session_id}'.",
            "telemetry_rate_hz": 10,
        })

        while True:
            # Wait for messages from client (e.g. ping, scrub, play)
            data_text = await websocket.receive_text()
            try:
                msg = json.loads(data_text)
            except Exception:
                msg = {"action": data_text}

            action = msg.get("action", msg.get("type", "ping"))

            if action == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "session_id": session_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
            elif action in ("request_telemetry", "seek", "play"):
                # Respond with current telemetry snapshot
                target_frame = msg.get("frame_id", 121418)
                await websocket.send_json({
                    "type": "telemetry_update",
                    "session_id": session_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "current_frame": target_frame,
                    "total_frames": 162000,
                    "fps": 60.0,
                    "cluster_load_percent": 74.0,
                    "inference_ms": 14.2,
                    "ai_confidence": 92.4,
                    "ball_velocity_kph": 86.4,
                    "ball_visibility": "HIGH",
                    "active_players_tracked": 22,
                    "optical_calib": "±0.08mm",
                })
            else:
                await websocket.send_json({
                    "type": "ack",
                    "session_id": session_id,
                    "received_action": action,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })

    except WebSocketDisconnect:
        ws_manager.disconnect(session_id, websocket)
    except Exception:
        ws_manager.disconnect(session_id, websocket)
