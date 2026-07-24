from datetime import date
from decimal import Decimal

from performance_cockpit.models import Measurement, MetricDefinition
from performance_cockpit.services.metrics import calculate_summary


def test_average_summary_without_target_has_no_deviation() -> None:
    metric = MetricDefinition(
        key="quality",
        display_name="Qualität",
        description="",
        unit="Prozent",
        aggregation="average",
    )
    measurements = [
        Measurement(
            metric_key="quality",
            organizational_unit="Nord",
            period_start=date(2026, 7, 1),
            period_end=date(2026, 7, 7),
            value=Decimal("90"),
            target_value=None,
            source="test.csv",
        ),
        Measurement(
            metric_key="quality",
            organizational_unit="Nord",
            period_start=date(2026, 7, 8),
            period_end=date(2026, 7, 14),
            value=Decimal("94"),
            target_value=None,
            source="test.csv",
        ),
    ]

    summary = calculate_summary(metric, "Nord", measurements)

    assert summary.value == Decimal("92.00")
    assert summary.target_value is None
    assert summary.attainment_percent is None
