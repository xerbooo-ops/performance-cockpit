import os
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from performance_cockpit.config import Settings
from performance_cockpit.database import create_database_engine
from performance_cockpit.models import Base, Measurement
from performance_cockpit.watcher import FileWatchService

CSV_TEMPLATE = "\n".join(
    [
        "metric_key,metric_name,description,unit,aggregation,organizational_unit,"
        "period_start,period_end,value,target_value",
        "calls,Calls,Anrufe,Anzahl,sum,EPA-7,2026-07-01,2026-07-01,{value},",
        "",
    ]
)


def test_watcher_imports_changed_file_and_persists_fingerprint(tmp_path) -> None:
    database_path = tmp_path / "watcher.db"
    report_path = tmp_path / "report.csv"
    settings = Settings(
        _env_file=None,
        database_url=f"sqlite+pysqlite:///{database_path}",
        watch_config_path=tmp_path / "watched-file.json",
    )
    engine = create_database_engine(settings)
    Base.metadata.create_all(engine)
    engine.dispose()
    report_path.write_text(CSV_TEMPLATE.format(value=110), encoding="utf-8")
    watcher = FileWatchService(settings)

    assert watcher.select_file(report_path) is True
    first_state = watcher.status()
    assert first_state.file_path == str(report_path)
    assert first_state.last_imported_at
    assert first_state.last_error == ""

    previous_modified = report_path.stat().st_mtime_ns
    report_path.write_text(CSV_TEMPLATE.format(value=125), encoding="utf-8")
    os.utime(report_path, ns=(previous_modified + 1_000_000, previous_modified + 1_000_000))
    assert watcher.check_once() is True

    engine = create_database_engine(settings)
    with Session(engine) as session:
        measurement = session.scalar(select(Measurement))
        assert measurement is not None
        assert measurement.value == Decimal("125")
    engine.dispose()

    restarted_watcher = FileWatchService(settings)
    assert restarted_watcher.status().file_path == str(report_path)
    assert restarted_watcher.check_once() is False


def test_watcher_retries_after_an_invalid_file_change(tmp_path) -> None:
    database_path = tmp_path / "watcher.db"
    report_path = tmp_path / "report.csv"
    settings = Settings(
        _env_file=None,
        database_url=f"sqlite+pysqlite:///{database_path}",
        watch_config_path=tmp_path / "watched-file.json",
    )
    engine = create_database_engine(settings)
    Base.metadata.create_all(engine)
    engine.dispose()
    report_path.write_text(CSV_TEMPLATE.format(value=110), encoding="utf-8")
    watcher = FileWatchService(settings)
    assert watcher.select_file(report_path) is True

    report_path.write_text("not a valid report", encoding="utf-8")
    assert watcher.check_once() is False
    assert watcher.status().last_error
