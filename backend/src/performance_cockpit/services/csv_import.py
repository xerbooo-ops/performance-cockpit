import csv
import io
from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    field_validator,
    model_validator,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from performance_cockpit.models import ImportBatch, Measurement, MetricDefinition
from performance_cockpit.schemas import ImportError, ImportResult

REQUIRED_COLUMNS = {
    "metric_key",
    "metric_name",
    "description",
    "unit",
    "aggregation",
    "organizational_unit",
    "period_start",
    "period_end",
    "value",
    "target_value",
}


class CsvMeasurementRow(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    metric_key: str = Field(pattern=r"^[a-z0-9_]+$", max_length=64)
    metric_name: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=1000)
    unit: str = Field(min_length=1, max_length=32)
    aggregation: Literal["sum", "average"]
    organizational_unit: str = Field(min_length=1, max_length=120)
    period_start: date
    period_end: date
    value: Decimal
    target_value: Decimal | None = None

    @field_validator("target_value", mode="before")
    @classmethod
    def empty_target_is_none(cls, value: object) -> object:
        return None if value == "" else value

    @model_validator(mode="after")
    def validate_period(self) -> "CsvMeasurementRow":
        if self.period_end < self.period_start:
            raise ValueError("period_end must be on or after period_start")
        return self


def _validation_errors(row_number: int, error: ValidationError) -> list[ImportError]:
    return [
        ImportError(
            row=row_number,
            field=str(item["loc"][0]) if item["loc"] else None,
            message=str(item["msg"]),
        )
        for item in error.errors()
    ]


def import_csv_text(session: Session, file_name: str, content: str) -> ImportResult:
    batch = ImportBatch(file_name=file_name, status="failed")
    session.add(batch)
    session.flush()

    reader = csv.DictReader(io.StringIO(content))
    missing_columns = REQUIRED_COLUMNS.difference(reader.fieldnames or [])
    if missing_columns:
        errors = [
            ImportError(
                row=1,
                field="header",
                message=f"Missing required columns: {', '.join(sorted(missing_columns))}",
            )
        ]
        batch.failed_rows = 1
        session.commit()
        return ImportResult(
            batch_id=batch.id,
            status="failed",
            total_rows=0,
            imported_rows=0,
            failed_rows=1,
            errors=errors,
        )

    imported_rows = 0
    errors: list[ImportError] = []
    total_rows = 0

    for row_number, raw_row in enumerate(reader, start=2):
        total_rows += 1
        try:
            row = CsvMeasurementRow.model_validate(raw_row)
        except ValidationError as error:
            errors.extend(_validation_errors(row_number, error))
            continue

        metric = session.get(MetricDefinition, row.metric_key)
        if metric is None:
            metric = MetricDefinition(
                key=row.metric_key,
                display_name=row.metric_name,
                description=row.description,
                unit=row.unit,
                aggregation=row.aggregation,
            )
            session.add(metric)
            session.flush([metric])
        else:
            metric.display_name = row.metric_name
            metric.description = row.description
            metric.unit = row.unit
            metric.aggregation = row.aggregation

        measurement = session.scalar(
            select(Measurement).where(
                Measurement.metric_key == row.metric_key,
                Measurement.organizational_unit == row.organizational_unit,
                Measurement.period_start == row.period_start,
                Measurement.period_end == row.period_end,
            )
        )
        if measurement is None:
            measurement = Measurement(
                metric_key=row.metric_key,
                organizational_unit=row.organizational_unit,
                period_start=row.period_start,
                period_end=row.period_end,
                value=row.value,
                target_value=row.target_value,
                source=file_name,
                import_batch_id=batch.id,
            )
            session.add(measurement)
        else:
            measurement.value = row.value
            measurement.target_value = row.target_value
            measurement.source = file_name
            measurement.import_batch_id = batch.id
        imported_rows += 1

    failed_rows = total_rows - imported_rows
    status = "completed_with_errors" if errors else "completed"
    batch.status = status
    batch.total_rows = total_rows
    batch.imported_rows = imported_rows
    batch.failed_rows = failed_rows
    session.commit()

    return ImportResult(
        batch_id=batch.id,
        status=status,
        total_rows=total_rows,
        imported_rows=imported_rows,
        failed_rows=failed_rows,
        errors=errors,
    )
