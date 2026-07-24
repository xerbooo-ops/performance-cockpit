from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/health", tags=["system"])


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str
    version: str


@router.get("", response_model=HealthResponse, summary="Readiness check")
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="performance-cockpit-api", version="1.0.2")
