from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from performance_cockpit.database import get_db
from performance_cockpit.models import MetricDefinition
from performance_cockpit.schemas import MeasurementRead, MetricDefinitionRead, MetricSummary
from performance_cockpit.services.metrics import get_summary, measurement_query

router = APIRouter(prefix="/metrics", tags=["metrics"])
DatabaseSession = Annotated[Session, Depends(get_db)]


@router.get("", response_model=list[MetricDefinitionRead])
def list_metrics(session: DatabaseSession) -> list[MetricDefinition]:
    return list(session.scalars(select(MetricDefinition).order_by(MetricDefinition.key)))


@router.get("/{metric_key}/measurements", response_model=list[MeasurementRead])
def list_measurements(
    metric_key: str,
    session: DatabaseSession,
    organizational_unit: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> list[MeasurementRead]:
    metric = session.get(MetricDefinition, metric_key)
    if metric is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Metric not found")
    return list(
        session.scalars(measurement_query(metric_key, organizational_unit, date_from, date_to))
    )


@router.get("/{metric_key}/summary", response_model=MetricSummary)
def read_summary(
    metric_key: str,
    session: DatabaseSession,
    organizational_unit: Annotated[str, Query(min_length=1, max_length=120)],
    date_from: date | None = None,
    date_to: date | None = None,
) -> MetricSummary:
    metric = session.get(MetricDefinition, metric_key)
    if metric is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Metric not found")
    summary = get_summary(session, metric, organizational_unit, date_from, date_to)
    if summary is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No measurements found for the selected filters",
        )
    return summary
