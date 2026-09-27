import numpy as np
from typing import List, Dict, Any, Tuple
from collections import deque
import cv2

class FormationService:
    def __init__(self, history_frames: int = 30, smoothing_window: int = 15):
        # Store recent pitch positions per track_id: {track_id: deque([(x, y), ...])}
        self.player_history = {}
        self.history_frames = history_frames
        
        # Store recent valid formations per team to smooth output
        self.formation_history = {"team_a": deque(maxlen=smoothing_window), "team_b": deque(maxlen=smoothing_window)}
        self.current_formations = {"team_a": "Formation unavailable", "team_b": "Formation unavailable"}
        self.current_confidences = {"team_a": 0.0, "team_b": 0.0}

    def update_player_history(self, track_id: int, pos: dict):
        if track_id not in self.player_history:
            self.player_history[track_id] = deque(maxlen=self.history_frames)
        self.player_history[track_id].append((pos['x'], pos['y']))

    def estimate_team_formation(self, team_name: str, players: List[dict]) -> Tuple[str, float]:
        """
        Estimate formation based on pitch coordinates.
        Requires at least 7 players. Uses 1D K-Means clustering along the pitch length (X-axis).
        """
        if len(players) < 7:
            return "Formation unavailable", 0.0
            
        x_coords = np.array([p['pitch_position']['x'] for p in players], dtype=np.float32)
        
        # Determine defending side based on median X (Pitch is 105m long)
        median_x = np.median(x_coords)
        defending_left = median_x < 52.5
        
        # We assume 3 structural bands (Defense, Midfield, Attack)
        k = 3
        
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        _, labels, centers = cv2.kmeans(x_coords.reshape(-1, 1), k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        
        # Group players by cluster
        counts = [0] * k
        for label in labels.flatten():
            counts[label] += 1
            
        # Sort clusters by center X coordinate
        centers_1d = centers.flatten()
        sorted_indices = np.argsort(centers_1d)
        
        if not defending_left:
            # Defending right side, so defense is the highest X
            sorted_indices = sorted_indices[::-1]
            
        formation_counts = [counts[idx] for idx in sorted_indices]
        
        # Format as string
        formation_str = "-".join(map(str, formation_counts))
        
        # Confidence is ratio of visible players to 10 (excluding keeper)
        confidence = min(1.0, len(players) / 10.0)
        
        return formation_str, confidence

    def process_frame(self, tracked_items: List[Any]) -> dict:
        """
        Process a frame of tracked items.
        Updates movement trails and estimates formations.
        Returns a dictionary to be attached to the WebSocket payload.
        """
        team_players = {"team_a": [], "team_b": []}
        
        # Filter and group mapped players
        for item in tracked_items:
            # item could be pydantic model or dict depending on pipeline stage
            is_dict = isinstance(item, dict)
            class_name = item['class_name'] if is_dict else item.class_name
            mapping_status = item.get('mapping_status') if is_dict else getattr(item, 'mapping_status', None)
            
            if class_name == "player" and mapping_status == "mapped":
                track_id = item['track_id'] if is_dict else item.track_id
                team = item.get('team') if is_dict else getattr(item, 'team', None)
                pitch_pos = item.get('pitch_position') if is_dict else getattr(item, 'pitch_position', None)
                
                if pitch_pos:
                    self.update_player_history(track_id, pitch_pos)
                    # Embed movement trail into the item for the frontend
                    trail = list(self.player_history[track_id])
                    if is_dict:
                        item['movement_trail'] = trail
                    else:
                        setattr(item, 'movement_trail', trail)
                        
                    if team in team_players:
                        # Store dict representation for easy access
                        team_players[team].append({
                            'track_id': track_id,
                            'pitch_position': pitch_pos
                        })

        # Estimate formation per team
        result = {}
        for team in ["team_a", "team_b"]:
            est_fmt, conf = self.estimate_team_formation(team, team_players[team])
            
            if est_fmt != "Formation unavailable":
                self.formation_history[team].append((est_fmt, conf))
            else:
                self.formation_history[team].append(None)
                
            # Smooth the output (majority vote in recent window)
            valid_history = [f for f in self.formation_history[team] if f is not None]
            if len(valid_history) >= len(self.formation_history[team]) * 0.3 and valid_history: # Need at least 30% valid in window
                formations = [f[0] for f in valid_history]
                most_common = max(set(formations), key=formations.count)
                avg_conf = sum(f[1] for f in valid_history if f[0] == most_common) / formations.count(most_common)
                
                self.current_formations[team] = most_common
                self.current_confidences[team] = round(float(avg_conf), 2)
            else:
                self.current_formations[team] = "Formation unavailable"
                self.current_confidences[team] = 0.0
                
            result[team] = self.current_formations[team]
            
        result["confidence"] = round((self.current_confidences["team_a"] + self.current_confidences["team_b"]) / 2.0, 2)
        
        return result
