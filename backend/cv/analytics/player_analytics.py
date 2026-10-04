import math
from typing import List, Dict, Any

class PlayerAnalyticsService:
    """
    Builds a real-data player analytics layer from tracking artifacts.
    Calculates distance, speed, movement samples, and aggregates events.
    """
    def __init__(self, fps: float = 30.0, max_tracking_gap_s: float = 1.0):
        self.fps = fps
        self.max_tracking_gap_s = max_tracking_gap_s
        self.players = {}
        
    def process_frame(self, frame_idx: int, timestamp: float, tracked_items: List[Any], events: List[Dict[str, Any]]):
        for item in tracked_items:
            # Distance only calculated for valid pitch coordinates
            if item.class_name == "player" and getattr(item, "pitch_position", None):
                pid = str(item.track_id)
                team = getattr(item, "team", "unknown")
                if pid not in self.players:
                    self.players[pid] = {
                        "player_id": pid,
                        "team": team,
                        "mapped_samples": 0,
                        "valid_duration_s": 0.0,
                        "distance_m": 0.0,
                        "speed_mps": 0.0,
                        "max_speed_mps": 0.0,
                        "positions": [],
                        "events": {
                            "touches": 0,
                            "short_touches": 0,
                            "possession_seconds": 0.0,
                            "possession_changes": 0,
                            "passes": 0,
                            "shots": 0,
                            "turnovers": 0,
                            "processed_ids": set()
                        },
                        "last_pos": None,
                        "last_timestamp": None,
                        "continuous_segments": 1,
                        "tracking_gaps": 0
                    }
                
                pdata = self.players[pid]
                pdata["mapped_samples"] += 1
                pos = item.pitch_position
                
                # Check pitch boundaries for heatmap to prevent invalid outliers
                # Standard pitch ~105x68, using generous bounds [-10 to 115, -10 to 78]
                is_valid_heatmap = -10 <= pos["x"] <= 115 and -10 <= pos["y"] <= 78
                
                if pdata["last_pos"] is not None and pdata["last_timestamp"] is not None:
                    dt = timestamp - pdata["last_timestamp"]
                    
                    if 0 < dt <= self.max_tracking_gap_s:
                        dx = pos["x"] - pdata["last_pos"]["x"]
                        dy = pos["y"] - pdata["last_pos"]["y"]
                        dist = math.hypot(dx, dy)
                        
                        speed = dist / dt
                        pdata["distance_m"] += dist
                        pdata["valid_duration_s"] += dt
                        
                        # Initialize EMA or smooth it
                        if pdata["speed_mps"] == 0.0:
                            pdata["speed_mps"] = speed
                        else:
                            alpha = 0.2
                            pdata["speed_mps"] = (alpha * speed) + ((1 - alpha) * pdata["speed_mps"])
                        
                        if pdata["speed_mps"] > pdata["max_speed_mps"]:
                            pdata["max_speed_mps"] = pdata["speed_mps"]
                            
                        # Only add to heatmap during continuous valid movement, throttled
                        if is_valid_heatmap and frame_idx % 5 == 0:
                            pdata["positions"].append({"x": round(pos["x"], 2), "y": round(pos["y"], 2)})
                    
                    elif dt > self.max_tracking_gap_s:
                        pdata["tracking_gaps"] += 1
                        pdata["continuous_segments"] += 1
                        # Do not add to distance or duration
                        
                elif is_valid_heatmap and frame_idx % 5 == 0:
                    pdata["positions"].append({"x": round(pos["x"], 2), "y": round(pos["y"], 2)})
                            
                pdata["last_pos"] = pos
                pdata["last_timestamp"] = timestamp

        for event in events:
            pid = str(event.get("player"))
            ev_id = event.get("id")
            
            if pid in self.players:
                # Deduplicate by event ID if available
                if ev_id and ev_id in self.players[pid]["events"]["processed_ids"]:
                    continue
                if ev_id:
                    self.players[pid]["events"]["processed_ids"].add(ev_id)
                    
                evt_type = event.get("event_type")
                if evt_type == "POSSESSION_CANDIDATE":
                    self.players[pid]["events"]["touches"] += 1
                    self.players[pid]["events"]["possession_seconds"] += (1.0 / self.fps)
                elif evt_type == "SHORT_TOUCH_POSSESSION":
                    self.players[pid]["events"]["short_touches"] += 1
                    self.players[pid]["events"]["touches"] += 1
                elif evt_type == "POSSESSION_CHANGE":
                    self.players[pid]["events"]["possession_changes"] += 1
                elif evt_type == "PASS_CANDIDATE" or evt_type == "PASS":
                    self.players[pid]["events"]["passes"] += 1
                elif evt_type == "SHOT_CANDIDATE" or evt_type == "SHOT":
                    self.players[pid]["events"]["shots"] += 1
                elif evt_type == "TURNOVER_CANDIDATE" or evt_type == "TURNOVER":
                    self.players[pid]["events"]["turnovers"] += 1

    def get_summary(self):
        players_list = []
        team_stats = {}
        
        total_samples = 0
        known_team_samples = 0

        for pid, data in self.players.items():
            duration = data["valid_duration_s"]
            mapped_samples = data["mapped_samples"]
            total_samples += mapped_samples
            if data["team"] != "unknown":
                known_team_samples += mapped_samples
            
            # Average speed is calculated from all valid movement intervals (total distance / total valid duration)
            avg_speed = (data["distance_m"] / duration) if duration > 0 else 0.0
            
            # Ensure max_speed >= average_speed mathematically if valid duration exists
            max_speed = data["max_speed_mps"]
            if max_speed < avg_speed:
                max_speed = avg_speed
                
            player_obj = {
                "player_id": pid,
                "team": data["team"],
                "tracking_duration": round(duration, 2),
                "estimated_distance_m": round(data["distance_m"], 2),
                "estimated_avg_speed_mps": round(avg_speed, 2),
                "estimated_max_speed_mps": round(max_speed, 2),
                "touches": data["events"]["touches"],
                "short_touches": data["events"]["short_touches"],
                "possession_seconds": round(data["events"]["possession_seconds"], 2),
                "passes": data["events"]["passes"],
                "shots": data["events"]["shots"],
                "turnovers": data["events"]["turnovers"],
                "data_quality": {
                    "mapped_samples": mapped_samples,
                    "tracking_gaps": data["tracking_gaps"],
                    "continuous_segments": data["continuous_segments"]
                },
                "heatmap": data["positions"]
            }
            players_list.append(player_obj)
            
            # Aggregate for team
            t = data["team"]
            if t not in team_stats:
                team_stats[t] = {
                    "team_name": t,
                    "estimated_distance_m": 0.0,
                    "possession_seconds": 0.0,
                    "touches": 0,
                    "passes": 0,
                    "shots": 0,
                    "turnovers": 0,
                    "unique_track_ids": 0
                }
            
            team_stats[t]["estimated_distance_m"] += data["distance_m"]
            team_stats[t]["possession_seconds"] += data["events"]["possession_seconds"]
            team_stats[t]["touches"] += data["events"]["touches"]
            team_stats[t]["passes"] += data["events"]["passes"]
            team_stats[t]["shots"] += data["events"]["shots"]
            team_stats[t]["turnovers"] += data["events"]["turnovers"]
            team_stats[t]["unique_track_ids"] += 1

        # Round team stats
        for t in team_stats:
            team_stats[t]["estimated_distance_m"] = round(team_stats[t]["estimated_distance_m"], 2)
            team_stats[t]["possession_seconds"] = round(team_stats[t]["possession_seconds"], 2)

        return {
            "metadata": {
                "unique_track_ids": len(self.players),
                "total_mapped_samples": total_samples,
                "known_team_samples_percentage": round((known_team_samples / max(1, total_samples)) * 100, 1)
            },
            "players": players_list,
            "teams": list(team_stats.values())
        }
