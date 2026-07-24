from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class MetricDefinitionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    key: str
    display_name: str
    description: str
    unit: str
    aggregation: Literal["sum", "average"]
    created_at: datetime


class MeasurementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    metric_key: str
    organizational_unit: str
    period_start: date
    period_end: date
    value: Decimal
    target_value: Decimal | None
    source: str


class MetricSummary(BaseModel):
    metric_key: str
    display_name: str
    organizational_unit: str
    period_start: date
    period_end: date
    unit: str
    aggregation: Literal["sum", "average"]
    value: Decimal
    target_value: Decimal | None
    deviation: Decimal | None
    attainment_percent: Decimal | None
    measurement_count: int


class ImportError(BaseModel):
    row: int
    field: str | None = None
    message: str


class ImportResult(BaseModel):
    batch_id: int
    status: Literal["completed", "completed_with_errors", "failed"]
    total_rows: int
    imported_rows: int
    failed_rows: int
    errors: list[ImportError] = Field(default_factory=list)


class DashboardFilters(BaseModel):
    organizational_units: list[str]
    period_start: date | None
    period_end: date | None


class DashboardData(BaseModel):
    organizational_unit: str
    period_start: date | None
    period_end: date | None
    last_imported_at: datetime | None
    source_files: list[str]
    summaries: list[MetricSummary]
