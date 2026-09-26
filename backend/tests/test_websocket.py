def test_websocket_connection_and_telemetry(client):
    session_id = "UCL-2024-MCI-RMA-F"
    with client.websocket_connect(f"/ws/analysis/{session_id}") as websocket:
        # Handshake
        initial_msg = websocket.receive_json()
        assert initial_msg["type"] == "connected"
        assert initial_msg["session_id"] == session_id

        # Send ping
        websocket.send_text('{"action": "ping"}')
        pong_msg = websocket.receive_json()
        assert pong_msg["type"] == "pong"
        assert pong_msg["session_id"] == session_id

        # Request telemetry
        websocket.send_text('{"action": "request_telemetry", "frame_id": 121418}')
        telem_msg = websocket.receive_json()
        assert telem_msg["type"] == "telemetry_update"
        assert telem_msg["current_frame"] == 121418
        assert telem_msg["ai_confidence"] == 92.4
        assert telem_msg["ball_velocity_kph"] == 86.4
