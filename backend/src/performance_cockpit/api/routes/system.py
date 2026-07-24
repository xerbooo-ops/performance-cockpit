from typing import Annotated, Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from performance_cockpit import __version__
from performance_cockpit.database import get_db
from performance_cockpit.models import ImportBatch, Measurement, MetricDefinition

router = APIRouter(prefix="/system", tags=["system"])


class Diagnostics(BaseModel):
    status: Literal["ok"]
    version: str
    database: Literal["ready"]
    local_only: Literal[True]
    metrics: int
    measurements: int
    imports: int


@router.get("/diagnostics", response_model=Diagnostics)
def diagnostics(session: Annotated[Session, Depends(get_db)]) -> Diagnostics:
    session.execute(text("SELECT 1"))
    return Diagnostics(
        status="ok",
        version=__version__,
        database="ready",
        local_only=True,
        metrics=session.scalar(select(func.count()).select_from(MetricDefinition)) or 0,
        measurements=session.scalar(select(func.count()).select_from(Measurement)) or 0,
        imports=session.scalar(select(func.count()).select_from(ImportBatch)) or 0,
    )
