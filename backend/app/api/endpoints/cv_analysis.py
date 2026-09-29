from fastapi import APIRouter
from backend.app.schemas.formation import FormationResponse
from backend.app.schemas.offside import OffsideResponse
from backend.cv.formation.service import FormationService
from backend.cv.offside.service import OffsideService

router = APIRouter()

formation_service = FormationService()
offside_service = OffsideService()


@router.get(
    "/{match_id}/formation",
    response_model=FormationResponse,
    tags=["Computer Vision (Pending Pipeline)"],
    summary="Get tactical formation analysis (CV Phase Placeholder)",
)
def get_formation(match_id: str):
    """
    Returns tactical line and player spatial formation.
    NOTE: Currently returns 'not_implemented' until the CV clustering and pitch homography models are trained and integrated.
    """
    return FormationResponse(
        status="not_implemented",
        module="FormationService",
        match_id=match_id,
        message="Not implemented. Tactical shape and team formation classification is currently streamed live via WebSocket, not this REST endpoint.",
        data={"match_id": match_id}
    )


@router.get(
    "/{match_id}/offside",
    response_model=OffsideResponse,
    tags=["Computer Vision (Pending Pipeline)"],
    summary="Get SAOT offside incident analysis (CV Phase Placeholder)",
)
def get_offside(match_id: str):
    """
    Returns Semi-Automated Offside Technology (SAOT) limb keypoint and axis analysis.
    NOTE: Currently returns 'not_implemented' until the limb keypoint estimation and kick-point models are integrated.
    """
    cv_res = offside_service.analyze_offside(match_id=match_id)
    return OffsideResponse(
        status=cv_res.status,
        module=cv_res.module_name,
        match_id=match_id,
        message=cv_res.message,
        data=cv_res.data,
    )
