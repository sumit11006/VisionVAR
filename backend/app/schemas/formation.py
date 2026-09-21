from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class FormationNode(BaseModel):
    jersey: int
    name: str
    role: str
    x: float
    y: float


class TeamFormation(BaseModel):
    formation_name: str
    lineup: List[FormationNode]
    compactness_rating: Optional[float] = None
    width_meters: Optional[float] = None
    depth_meters: Optional[float] = None


class FormationResponse(BaseModel):
    status: str = "not_implemented"
    module: str = "FormationService"
    match_id: str
    message: str = (
        "Formation detection pipeline is not implemented yet. "
        "Pitch spatial clustering and tactical line analysis will be integrated in the Computer Vision phase."
    )
    contract_specification: Dict[str, Any] = {
        "expected_payload": {
            "home_formation": "TeamFormation (formation_name, lineup[], compactness_rating, width_meters, depth_meters)",
            "away_formation": "TeamFormation (formation_name, lineup[], compactness_rating, width_meters, depth_meters)",
            "centroid_clustering_confidence": "float (0.0 - 1.0)",
        }
    }
    data: Optional[Dict[str, Any]] = None
