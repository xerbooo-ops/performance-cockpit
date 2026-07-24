import sqlite3
from datetime import date
from decimal import Decimal
from io import BytesIO
from pathlib import Path

import pytest
from alembic import command
from fastapi.testclient import TestClient
from openpyxl import load_workbook
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session

from performance_cockpit.config import Settings
from performance_cockpit.database import initialize_database, migration_config
from performance_cockpit.models import Base, ImportBatch, Measurement, MetricDefinition
from performance_cockpit.services.data_management import (
    create_backup,
    export_dashboard_pdf,
    export_measurements_csv,
    export_measurements_xlsx,
    reset_data,
    restore_backup,
    sqlite_database_path,
)


def test_history_export_and_confirmed_reset(client: TestClient) -> None:
    content = "\n".join(
        [
            "metric_key,metric_name,description,unit,aggregation,organizational_unit,"
            "period_start,period_end,value,target_value",
            "sales,Umsatz,Umsatz,Euro,sum,Team A,2026-07-01,2026-07-31,1200,1000",
        ]
    )
    client.post("/api/v1/imports/file", files={"file": ("july.csv", content, "text/csv")})

    history = client.get("/api/v1/data/imports")
    export = client.get("/api/v1/data/export.csv")
    xlsx = client.get("/api/v1/data/export.xlsx")
    pdf = client.get(
        "/api/v1/data/report.pdf",
        params={"organizational_unit": "Team A"},
    )
    rejected_reset = client.post("/api/v1/data/reset", json={"confirmation": "delete"})
    accepted_reset = client.post("/api/v1/data/reset", json={"confirmation": "DELETE"})

    assert history.status_code == 200
    assert history.json()[0]["file_name"] == "july.csv"
    assert history.json()[0]["errors"] == []
    assert export.status_code == 200
    assert "sales,Umsatz,Umsatz,Euro,sum,Team A" in export.text
    workbook = load_workbook(BytesIO(xlsx.content), read_only=True)
    assert workbook["Kennzahlen"]["A2"].value == "sales"
    assert xlsx.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert pdf.content.startswith(b"%PDF-1.4")
    assert b"Ziel" not in pdf.content
    assert pdf.headers["content-type"] == "application/pdf"
    assert rejected_reset.status_code == 422
    assert accepted_reset.status_code == 200
    assert client.get("/api/v1/metrics/dashboard/filters").json()["organizational_units"] == []


def test_backup_and_restore_round_trip(tmp_path: Path) -> None:
    database_path = tmp_path / "cockpit.db"
    engine = create_engine(f"sqlite+pysqlite:///{database_path}")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        metric = MetricDefinition(
            key="quality",
            display_name="Qualität",
            description="",
            unit="Prozent",
            aggregation="average",
        )
        session.add(metric)
        session.add(
            ImportBatch(
                file_name="quality.xlsx",
                status="completed",
                total_rows=1,
                imported_rows=1,
                failed_rows=0,
            )
        )
        session.flush()
        session.add(
            Measurement(
                metric_key="quality",
                organizational_unit="Team A",
                period_start=date(2026, 7, 1),
                period_end=date(2026, 7, 31),
                value=Decimal("95"),
                target_value=Decimal("90"),
                source="quality.xlsx",
            )
        )
        session.commit()
        assert "quality,Qualität" in export_measurements_csv(session)
        assert export_measurements_xlsx(session).startswith(b"PK")
        assert export_dashboard_pdf(session, "Team A").startswith(b"%PDF-1.4")

    backup = create_backup(database_path)
    with Session(engine) as session:
        reset_data(session)
    engine.dispose()
    restore_backup(database_path, backup)

    restored_engine = create_engine(f"sqlite+pysqlite:///{database_path}")
    with Session(restored_engine) as session:
        assert session.get(MetricDefinition, "quality") is not None
    restored_engine.dispose()


def test_invalid_backup_is_rejected(tmp_path: Path) -> None:
    database_path = tmp_path / "cockpit.db"
    database_path.touch()

    with pytest.raises(ValueError, match="valid SQLite"):
        restore_backup(database_path, b"not a database")


def test_release_04_database_is_adopted_and_migrated(tmp_path: Path) -> None:
    database_path = tmp_path / "legacy.db"
    settings = Settings(
        _env_file=None,
        database_url=f"sqlite+pysqlite:///{database_path}",
    )
    migrations = Path(__file__).parents[1] / "migrations"
    config = migration_config(settings, migrations)
    command.upgrade(config, "0001")
    with sqlite3.connect(database_path) as connection:
        connection.execute("DROP TABLE alembic_version")

    initialize_database(settings, migrations)

    engine = create_engine(settings.database_url)
    assert "error_details" in {
        column["name"] for column in inspect(engine).get_columns("import_batches")
    }
    assert sqlite_database_path(settings.database_url) == database_path
    engine.dispose()
