from typing import Optional, Dict, Any
from pydantic import BaseModel


class OffsideResponse(BaseModel):
    status: str = "not_implemented"
    module: str = "OffsideService"
    match_id: str
    message: str = (
        "Semi-Automated Offside Technology (SAOT) limb keypoint & pitch homography pipeline is not implemented yet. "
        "Skeleton keypoints, attacker/defender axis projection, and kick-point detection will be integrated in the Computer Vision phase."
    )
    contract_specification: Dict[str, Any] = {
        "expected_payload": {
            "incident_id": "string",
            "frame_id": "int",
            "timecode": "string",
            "verdict": "'ONSIDE' | 'OFFSIDE'",
            "margin_meters": "float",
            "uncertainty_meters": "float",
            "attacker": "OffsidePlayer (jersey, name, team, body_part_datum, axis_meters, centroid)",
            "defender": "OffsidePlayer (jersey, name, team, body_part_datum, axis_meters, centroid)",
            "ball_contact": "BallContact (timecode, frame_id, ball_speed_kph, confirmed)",
        }
    }
    data: Optional[Dict[str, Any]] = None
