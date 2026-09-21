from typing import Optional, Any
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"
    service: str = "VisionVAR Backend"
    database: str = "connected"
    cv_pipeline: str = "standby"


class CVNotImplementedResponse(BaseModel):
    status: str = "not_implemented"
    module: str
    message: str
    details: Optional[str] = None
    contract_version: str = "v1"
    data: Optional[Any] = None
