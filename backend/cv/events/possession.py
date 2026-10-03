import math
from typing import List, Dict, Optional, Any

class PossessionService:
    """
    Tracks and infers ball possession by evaluating continuous spatial proximity 
    between tracked players and the ball over time, supporting both firm possession
    and one-touch / short-touch passing sequences.
    """
    def __init__(self, 
                 distance_threshold_m: float = 2.5, 
                 firm_possession_frames: int = 5,
                 short_touch_min_frames: int = 1,
                 short_touch_max_frames: int = 4,
                 max_ball_travel_gap_frames: int = 60):
                 
        self.distance_threshold = distance_threshold_m
        self.firm_possession_frames = firm_possession_frames
        self.short_touch_min_frames = short_touch_min_frames
        self.short_touch_max_frames = short_touch_max_frames
        self.max_ball_travel_gap_frames = max_ball_travel_gap_frames
        
        # State tracking
        self.current_possessor_id = None
        self.current_team = "unknown"
        self.possession_frames = 0
        self.has_contact_evidence = False
        
        self.last_known_possessor = None
        self.last_known_team = "unknown"
        self.frames_since_last_possession = 0
        
    def reset(self):
        self.current_possessor_id = None
        self.current_team = "unknown"
        self.possession_frames = 0
        self.has_contact_evidence = False
        self.last_known_possessor = None
        self.last_known_team = "unknown"
        self.frames_since_last_possession = 0

    def process(self, frame_idx: int, timestamp: float, tracked_items: List[Any], ball_state: Dict[str, Any], ball_contact_event: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        events = []
        
        if not ball_state or ball_state.get("state") not in ("tracked", "reacquired") or not ball_state.get("pitch_position"):
            # Ball lost - we keep the state suspended.
            self.frames_since_last_possession += 1
            return events
            
        ball_pos = ball_state["pitch_position"]
        bx, by = ball_pos["x"], ball_pos["y"]
        
        closest_player = None
        min_dist = float('inf')
        
        for item in tracked_items:
            if item.class_name == "player" and getattr(item, "pitch_position", None):
                px, py = item.pitch_position["x"], item.pitch_position["y"]
                dist = math.hypot(px - bx, py - by)
                if dist < min_dist:
                    min_dist = dist
                    closest_player = item
                    
        is_contact_frame = False
        if ball_contact_event and ball_contact_event.get("state") in ("possible", "confirmed"):
            is_contact_frame = True
            
        if closest_player and min_dist <= self.distance_threshold:
            # Player near ball
            player_id = closest_player.track_id
            team = getattr(closest_player, "team", "unknown")
            
            if self.current_possessor_id == player_id:
                self.possession_frames += 1
                if is_contact_frame:
                    self.has_contact_evidence = True
            else:
                # We had someone else, and now a new person is closest. Let's resolve the old one if it was a short touch
                if self.current_possessor_id is not None:
                    # Player changed without a gap
                    short_touch_events = self._resolve_short_touch(frame_idx, timestamp, min_dist)
                    events.extend(short_touch_events)
                
                # Start new potential possession
                self.current_possessor_id = player_id
                self.current_team = team
                self.possession_frames = 1
                self.has_contact_evidence = is_contact_frame
                
            # If we just hit firm possession frames
            if self.possession_frames == self.firm_possession_frames:
                events.extend(self._establish_possession(player_id, team, frame_idx, timestamp, min_dist, "firm_possession"))
                
        else:
            # Nobody is close enough. Did we just finish a short touch?
            if self.current_possessor_id is not None:
                short_touch_events = self._resolve_short_touch(frame_idx, timestamp, min_dist)
                events.extend(short_touch_events)
                
            self.current_possessor_id = None
            self.possession_frames = 0
            self.has_contact_evidence = False
            self.frames_since_last_possession += 1
            
        return events
        
    def _resolve_short_touch(self, frame_idx: int, timestamp: float, dist: float) -> List[Dict[str, Any]]:
        events = []
        # Was the previous interaction a short touch?
        if self.short_touch_min_frames <= self.possession_frames <= self.short_touch_max_frames:
            # Need additional evidence: did the ball physically contact them?
            if self.has_contact_evidence:
                events.extend(self._establish_possession(self.current_possessor_id, self.current_team, frame_idx, timestamp, dist, "short_touch"))
        return events
        
    def _establish_possession(self, player_id: int, team: str, frame_idx: int, timestamp: float, dist: float, reason: str) -> List[Dict[str, Any]]:
        events = []
        if self.last_known_possessor != player_id:
            # It's a new possessor
            
            # If it's a pass between the same team (Tiki-Taka)
            is_same_team_pass = (self.last_known_team == team and self.last_known_team not in ("unknown", None))
            
            # If it's a turnover to the other team
            is_turnover = (self.last_known_team not in ("unknown", None) and 
                           team not in ("unknown", None) and 
                           self.last_known_team != team)
            
            # Only trigger turnover if the gap wasn't too massive (to prevent treating random ball loss as a turnover)
            gap_too_large = self.frames_since_last_possession > self.max_ball_travel_gap_frames
            
            if is_turnover and not gap_too_large:
                event_type = "TURNOVER_CANDIDATE"
                status = "candidate"
            elif is_same_team_pass and reason == "short_touch":
                event_type = "SHORT_TOUCH_POSSESSION"
                status = "confirmed"
            else:
                event_type = "POSSESSION_CHANGE"
                status = "confirmed"
                
            # If it's a short touch, we might also trigger a PASS_CANDIDATE conceptually if it goes from A->B, but we'll let 
            # EventDetectionService handle Pass events separately, or we emit it here as a possession linkage.
            
            event = {
                "event_type": event_type,
                "frame": frame_idx,
                "timestamp": timestamp,
                "player": str(player_id),
                "team": team,
                "status": status,
                "confidence": 0.85,
                "metadata": {
                    "distance_m": round(dist, 2),
                    "previous_player": self.last_known_possessor,
                    "previous_team": self.last_known_team,
                    "reason": reason,
                    "gap_frames": self.frames_since_last_possession
                }
            }
            events.append(event)
            
            self.last_known_possessor = player_id
            self.last_known_team = team
            self.frames_since_last_possession = 0
            
        return events
