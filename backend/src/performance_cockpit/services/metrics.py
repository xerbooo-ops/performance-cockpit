from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from performance_cockpit.models import Measurement, MetricDefinition
from performance_cockpit.schemas import MetricSummary

PRECISION = Decimal("0.01")


def measurement_query(
    metric_key: str,
    organizational_unit: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> Select[tuple[Measurement]]:
    query = select(Measurement).where(Measurement.metric_key == metric_key)
    if organizational_unit:
        query = query.where(Measurement.organizational_unit == organizational_unit)
    if date_from:
        query = query.where(Measurement.period_start >= date_from)
    if date_to:
        query = query.where(Measurement.period_end <= date_to)
    return query.order_by(Measurement.period_start, Measurement.organizational_unit)


def calculate_summary(
    metric: MetricDefinition,
    organizational_unit: str,
    measurements: list[Measurement],
) -> MetricSummary:
    values = [item.value for item in measurements]
    targets = [item.target_value for item in measurements if item.target_value is not None]

    if metric.aggregation == "average":
        value = sum(values, Decimal()) / len(values)
        target = sum(targets, Decimal()) / len(targets) if targets else None
    else:
        value = sum(values, Decimal())
        target = sum(targets, Decimal()) if targets else None

    rounded_value = value.quantize(PRECISION, rounding=ROUND_HALF_UP)
    rounded_target = target.quantize(PRECISION, rounding=ROUND_HALF_UP) if target else target
    deviation = (
        (rounded_value - rounded_target).quantize(PRECISION, rounding=ROUND_HALF_UP)
        if rounded_target is not None
        else None
    )
    attainment = (
        ((rounded_value / rounded_target) * 100).quantize(PRECISION, rounding=ROUND_HALF_UP)
        if rounded_target not in (None, Decimal())
        else None
    )

    return MetricSummary(
        metric_key=metric.key,
        display_name=metric.display_name,
        organizational_unit=organizational_unit,
        period_start=min(item.period_start for item in measurements),
        period_end=max(item.period_end for item in measurements),
        unit=metric.unit,
        aggregation=metric.aggregation,
        value=rounded_value,
        target_value=rounded_target,
        deviation=deviation,
        attainment_percent=attainment,
        measurement_count=len(measurements),
    )


def get_summary(
    session: Session,
    metric: MetricDefinition,
    organizational_unit: str,
    date_from: date | None,
    date_to: date | None,
) -> MetricSummary | None:
    measurements = list(
        session.scalars(measurement_query(metric.key, organizational_unit, date_from, date_to))
    )
    if not measurements:
        return None
    return calculate_summary(metric, organizational_unit, measurements)
