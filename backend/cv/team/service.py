import numpy as np
import cv2
from typing import Dict, List, Optional
from collections import defaultdict
from backend.app.schemas.detection import TrackedItem

class TeamClassificationService:
    def __init__(self):
        # track_id -> list of predictions (e.g. ['team_a', 'team_a', 'team_b'])
        self.history: Dict[int, List[str]] = defaultdict(list)
        self.history_size = 5
        
        # Store the dominant HSV of each track to compute centroids
        self.track_colors = {}
        # The two team centroids (np array of shape (2, 3))
        self.team_centroids = None 
        # Has enough data been collected to start clustering?
        self.is_clustering_ready = False

    def extract_jersey_features(self, player_crop: np.ndarray):
        if player_crop is None or player_crop.size == 0:
            return None

        h, w, _ = player_crop.shape
        if h < 10 or w < 10:
            return None

        # Crop to upper body (upper 20% to 50% to avoid head and shorts)
        # Also crop sides to avoid background
        y1, y2 = int(h * 0.2), int(h * 0.5)
        x1, x2 = int(w * 0.2), int(w * 0.8)
        
        jersey_crop = player_crop[y1:y2, x1:x2]
        if jersey_crop.size == 0:
            return None

        # Convert to HSV
        hsv = cv2.cvtColor(jersey_crop, cv2.COLOR_BGR2HSV)
        
        mean_h = np.mean(hsv[:, :, 0])
        mean_s = np.mean(hsv[:, :, 1])
        mean_v = np.mean(hsv[:, :, 2])

        # Filter out referees/staff (usually white/grey/black - low saturation or very bright/dark)
        # Filter out grass (green hue ~30-80)
        if mean_s < 50 and mean_v > 150:
            return "referee"
        if 35 < mean_h < 85: # Grass green
            return "grass"

        return np.array([mean_h, mean_s, mean_v], dtype=np.float32)

    def _update_clusters(self):
        # Only cluster if we have at least 5 distinct tracks to form 2 teams
        valid_tracks = list(self.track_colors.values())
        if len(valid_tracks) < 5:
            return

        data = np.vstack(valid_tracks)
        
        # Run K-Means (K=2)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
        _, labels, centers = cv2.kmeans(data, 2, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        
        self.team_centroids = centers
        self.is_clustering_ready = True
        
        # Log the discovered colors occasionally
        if len(valid_tracks) % 50 == 0:
            def hsv_to_name(hsv):
                h, s, v = hsv
                if s < 50: return "White/Grey"
                if h < 15 or h > 165: return "Red"
                if 15 <= h < 35: return "Yellow/Orange"
                if 35 <= h < 85: return "Green"
                if 85 <= h < 135: return "Blue"
                if 135 <= h <= 165: return "Purple/Pink"
                return "Unknown Color"
            
            color_a = hsv_to_name(centers[0])
            color_b = hsv_to_name(centers[1])
            print(f"[TeamClassifier] Dynamically assigned Team A -> {color_a}, Team B -> {color_b}")
            with open("discovered_colors.txt", "w") as f:
                f.write(f"Team A: {color_a}\nTeam B: {color_b}\n")

    def predict_team(self, track_id: int, frame_bgr: np.ndarray, bbox: dict) -> tuple[str, float]:
        x1, y1 = max(0, int(bbox.x1)), max(0, int(bbox.y1))
        x2, y2 = int(bbox.x2), int(bbox.y2)
        
        player_crop = frame_bgr[y1:y2, x1:x2]
        features = self.extract_jersey_features(player_crop)

        if features is None or isinstance(features, str):
            # Referee, Grass, or too small
            predicted_team = "unknown"
        else:
            # Save feature to track memory (moving average)
            if track_id in self.track_colors:
                self.track_colors[track_id] = self.track_colors[track_id] * 0.8 + features * 0.2
            else:
                self.track_colors[track_id] = features
                
            self._update_clusters()

            if not self.is_clustering_ready:
                predicted_team = "unknown"
            else:
                # Find closest centroid (L2 distance)
                dist_a = np.linalg.norm(features - self.team_centroids[0])
                dist_b = np.linalg.norm(features - self.team_centroids[1])
                
                if dist_a < dist_b:
                    predicted_team = "team_a"
                else:
                    predicted_team = "team_b"

        # Update history
        self.history[track_id].append(predicted_team)
        if len(self.history[track_id]) > self.history_size:
            self.history[track_id].pop(0)

        # Smooth prediction (majority voting)
        valid_votes = [t for t in self.history[track_id] if t != "unknown"]
        if not valid_votes:
            return "unknown", 0.0

        counts = {t: valid_votes.count(t) for t in set(valid_votes)}
        best_team = max(counts, key=counts.get)
        confidence = counts[best_team] / len(self.history[track_id])

        if confidence < 0.4:
            return "unknown", 0.0

        return best_team, round(confidence, 2)

    def process_tracked_items(self, items: List[TrackedItem], frame_bgr: np.ndarray) -> List[TrackedItem]:
        for item in items:
            if item.class_name == "player":
                team, conf = self.predict_team(item.track_id, frame_bgr, item.bbox)
                item.team = team
                item.team_confidence = conf if team != "unknown" else None
        return items
