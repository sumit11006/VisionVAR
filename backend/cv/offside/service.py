from typing import List, Dict, Any, Optional
import numpy as np

class OffsideAnalysisService:
    def __init__(self):
        pass

    def determine_attacking_direction(self, team: str, team_players: List[Dict[str, Any]]) -> str:
        if len(team_players) < 5:
            return "unknown"
        
        x_coords = [p["pitch_position"]["x"] for p in team_players if p.get("pitch_position")]
        if not x_coords:
            return "unknown"
            
        median_x = np.median(x_coords)
        if median_x < 52.5: # Defending left, attacking right
            return "positive_x"
        else: # Defending right, attacking left
            return "negative_x"

    def analyze(self, ball_contact: Dict[str, Any], tracked_items: List[Any], timestamp: float, frame: int) -> Optional[Dict[str, Any]]:
        # Only analyze if there is a possible ball contact
        if ball_contact.get("state") != "possible":
            return None
            
        # Group players by team with pitch positions
        team_players = {"team_a": [], "team_b": []}
        for item in tracked_items:
            is_dict = isinstance(item, dict)
            class_name = item.get("class_name") if is_dict else getattr(item, "class_name", None)
            mapping_status = item.get("mapping_status") if is_dict else getattr(item, "mapping_status", None)
            
            if class_name == "player" and mapping_status == "mapped":
                team = item.get("team") if is_dict else getattr(item, "team", None)
                if team in team_players:
                    team_players[team].append({
                        "track_id": item.get("track_id") if is_dict else getattr(item, "track_id"),
                        "team": team,
                        "pitch_position": item.get("pitch_position") if is_dict else getattr(item, "pitch_position")
                    })

        dir_a = self.determine_attacking_direction("team_a", team_players["team_a"])
        dir_b = self.determine_attacking_direction("team_b", team_players["team_b"])
        
        # Build second last defender line for Team B (defending against Team A)
        line_b = {"status": "unavailable", "x": 0.0, "defender_id": None}
        if len(team_players["team_b"]) >= 2 and dir_a != "unknown":
            sorted_b = sorted(team_players["team_b"], key=lambda p: p["pitch_position"]["x"], reverse=(dir_a == "positive_x"))
            second_last = sorted_b[1]
            line_b = {"status": "available", "x": second_last["pitch_position"]["x"], "defender_id": second_last["track_id"]}

        # Build second last defender line for Team A (defending against Team B)
        line_a = {"status": "unavailable", "x": 0.0, "defender_id": None}
        if len(team_players["team_a"]) >= 2 and dir_b != "unknown":
            sorted_a = sorted(team_players["team_a"], key=lambda p: p["pitch_position"]["x"], reverse=(dir_b == "positive_x"))
            second_last = sorted_a[1]
            line_a = {"status": "available", "x": second_last["pitch_position"]["x"], "defender_id": second_last["track_id"]}
            
        players_status = []
        for p in team_players["team_a"]:
            status = "unavailable"
            if line_b["status"] == "available":
                if dir_a == "positive_x":
                    status = "potentially_offside" if p["pitch_position"]["x"] > line_b["x"] else "onside"
                else:
                    status = "potentially_offside" if p["pitch_position"]["x"] < line_b["x"] else "onside"
            players_status.append({
                "track_id": p["track_id"],
                "team": "team_a",
                "pitch_x": p["pitch_position"]["x"],
                "status": status
            })
            
        for p in team_players["team_b"]:
            status = "unavailable"
            if line_a["status"] == "available":
                if dir_b == "positive_x":
                    status = "potentially_offside" if p["pitch_position"]["x"] > line_a["x"] else "onside"
                else:
                    status = "potentially_offside" if p["pitch_position"]["x"] < line_a["x"] else "onside"
            players_status.append({
                "track_id": p["track_id"],
                "team": "team_b",
                "pitch_x": p["pitch_position"]["x"],
                "status": status
            })

        ai_assessment = "INSUFFICIENT EVIDENCE"
        if line_b["status"] == "available" or line_a["status"] == "available":
            ai_assessment = "ONSIDE"
            for p in players_status:
                if p["status"] == "potentially_offside":
                    ai_assessment = "POTENTIAL OFFSIDE"
                    break

        return {
            "status": "candidate",
            "ball_contact": ball_contact,
            "team_a_attacking_dir": dir_a,
            "team_b_attacking_dir": dir_b,
            "offside_line_against_a": line_b,
            "offside_line_against_b": line_a,
            "players": players_status,
            "ai_assessment": ai_assessment,
            "evidence": "SUFFICIENT FOR GEOMETRIC REVIEW" if ai_assessment != "INSUFFICIENT EVIDENCE" else "INSUFFICIENT EVIDENCE"
        }

from backend.cv.base import BaseOffsideService, CVResult

class OffsideService(BaseOffsideService):
    @property
    def module_name(self) -> str:
        return "OffsideService"

    def is_ready(self) -> bool:
        return False

    def analyze_offside(self, match_id: str, incident_frame: Optional[int] = None) -> CVResult:
        return CVResult(
            status="not_implemented",
            module_name=self.module_name,
            message="Semi-Automated Offside Technology (SAOT) 3D keypoint projection is not implemented yet. Pipeline will be configured in the Computer Vision phase.",
            data={
                "match_id": match_id,
                "incident_frame": incident_frame,
                "pending_components": [
                    "Limb keypoint skeletal estimation (HRNet/YOLO-Pose)",
                    "Kick-point contact frame detection",
                    "3D virtual offside line projection",
                ],
            },
        )
