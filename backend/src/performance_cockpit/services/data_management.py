import csv
import io
import json
import sqlite3
import tempfile
from pathlib import Path

from sqlalchemy import delete, select
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from performance_cockpit.models import ImportBatch, Measurement, MetricDefinition
from performance_cockpit.schemas import ImportBatchRead, ImportError

EXPORT_COLUMNS = [
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
    "source",
]
REQUIRED_BACKUP_TABLES = {"metric_definitions", "measurements", "import_batches"}


def sqlite_database_path(database_url: str) -> Path:
    url = make_url(database_url)
    if url.drivername != "sqlite+pysqlite" or not url.database or url.database == ":memory:":
        raise ValueError("Local data management requires a file-based SQLite database")
    return Path(url.database)


def import_history(session: Session, limit: int = 20) -> list[ImportBatchRead]:
    batches = list(
        session.scalars(select(ImportBatch).order_by(ImportBatch.created_at.desc()).limit(limit))
    )
    return [
        ImportBatchRead(
            id=batch.id,
            file_name=batch.file_name,
            status=batch.status,
            total_rows=batch.total_rows,
            imported_rows=batch.imported_rows,
            failed_rows=batch.failed_rows,
            created_at=batch.created_at,
            errors=[
                ImportError.model_validate(error)
                for error in json.loads(batch.error_details or "[]")
            ],
        )
        for batch in batches
    ]


def export_measurements_csv(session: Session) -> str:
    measurements = list(
        session.scalars(
            select(Measurement)
            .join(Measurement.metric)
            .order_by(
                Measurement.metric_key,
                Measurement.organizational_unit,
                Measurement.period_start,
            )
        )
    )
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=EXPORT_COLUMNS, lineterminator="\n")
    writer.writeheader()
    for item in measurements:
        writer.writerow(
            {
                "metric_key": item.metric_key,
                "metric_name": item.metric.display_name,
                "description": item.metric.description,
                "unit": item.metric.unit,
                "aggregation": item.metric.aggregation,
                "organizational_unit": item.organizational_unit,
                "period_start": item.period_start.isoformat(),
                "period_end": item.period_end.isoformat(),
                "value": item.value,
                "target_value": item.target_value if item.target_value is not None else "",
                "source": item.source,
            }
        )
    return output.getvalue()


def create_backup(database_path: Path) -> bytes:
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temporary:
        backup_path = Path(temporary.name)
    try:
        with (
            sqlite3.connect(database_path) as source,
            sqlite3.connect(backup_path) as destination,
        ):
            source.backup(destination)
        return backup_path.read_bytes()
    finally:
        backup_path.unlink(missing_ok=True)


def validate_backup(backup_path: Path) -> None:
    try:
        with sqlite3.connect(backup_path) as connection:
            integrity = connection.execute("PRAGMA integrity_check").fetchone()
            tables = {
                row[0]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                ).fetchall()
            }
    except sqlite3.DatabaseError as error:
        raise ValueError("Backup is not a valid SQLite database") from error
    if not integrity or integrity[0] != "ok":
        raise ValueError("Backup database failed its integrity check")
    if not REQUIRED_BACKUP_TABLES.issubset(tables):
        raise ValueError("Backup does not contain Performance Cockpit data")


def restore_backup(database_path: Path, content: bytes) -> None:
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temporary:
        temporary.write(content)
        backup_path = Path(temporary.name)
    try:
        validate_backup(backup_path)
        with (
            sqlite3.connect(backup_path) as source,
            sqlite3.connect(database_path) as destination,
        ):
            source.backup(destination)
    finally:
        backup_path.unlink(missing_ok=True)


def reset_data(session: Session) -> None:
    session.execute(delete(Measurement))
    session.execute(delete(MetricDefinition))
    session.execute(delete(ImportBatch))
    session.commit()
