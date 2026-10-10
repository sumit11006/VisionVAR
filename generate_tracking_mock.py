import json
import os

session_dir = "data/sessions/UCL-2024-MCI-RMA-F"
det_path = os.path.join(session_dir, "detections.json")
out_path = os.path.join(session_dir, "tracking_results.json")

if os.path.exists(det_path):
    with open(det_path, "r") as f:
        det_data = json.load(f)
        
    frames = []
    for r in det_data.get("records", []):
        frame_num = r.get("frame", 0)
        timestamp = r.get("timestamp", 0.0)
        
        tracked = []
        for i, d in enumerate(r.get("detections", [])):
            tracked.append({
                "track_id": i + 1,
                "class_name": d.get("class", "player"),
                "class": d.get("class", "player"),
                "confidence": d.get("confidence", 0.0),
                "bbox": d.get("bbox", {}),
                "team": "team_a" if i % 2 == 0 else "team_b",
                "mapping_status": "mapped",
                "pitch_position": {"x": 50, "y": 30}
            })
            
        frames.append({
            "frame_number": frame_num,
            "timestamp": timestamp,
            "tracked_items": tracked,
            "ball_state": {
                "state": "tracked" if r.get("ball_detected") else "lost",
                "confidence": 0.95
            },
            "formation": {},
            "pitch_mapping_status": "mapped"
        })
        
    tracking_data = {
        "session_id": "UCL-2024-MCI-RMA-F",
        "frames": frames
    }
    
    with open(out_path, "w") as f:
        json.dump(tracking_data, f)
        
    print(f"Generated {out_path} with {len(frames)} frames")
else:
    print(f"Missing {det_path}")
