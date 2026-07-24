import json
import threading
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

import structlog
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from performance_cockpit.config import Settings
from performance_cockpit.database import create_database_engine
from performance_cockpit.services.csv_import import import_csv_text
from performance_cockpit.services.file_import import import_xlsx_bytes


@dataclass
class WatchState:
    file_path: str = ""
    modified_ns: int = 0
    size: int = 0
    last_imported_at: str = ""
    last_error: str = ""


class FileWatchService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.config_path = settings.watch_config_path
        self.interval_seconds = settings.watch_interval_seconds
        self._state = self._load_state()
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._logger = structlog.get_logger()

    def _load_state(self) -> WatchState:
        try:
            payload = json.loads(self.config_path.read_text(encoding="utf-8"))
            return WatchState(
                **{key: payload[key] for key in WatchState.__dataclass_fields__ if key in payload}
            )
        except (OSError, ValueError, TypeError):
            return WatchState()

    def _save_state(self) -> None:
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.config_path.with_suffix(".tmp")
        temporary_path.write_text(
            json.dumps(asdict(self._state), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temporary_path.replace(self.config_path)

    def status(self) -> WatchState:
        with self._lock:
            return WatchState(**asdict(self._state))

    def select_file(self, file_path: Path) -> bool:
        resolved = file_path.expanduser().resolve()
        if resolved.suffix.lower() not in {".csv", ".xlsx"} or not resolved.is_file():
            raise ValueError("Bitte eine vorhandene CSV- oder XLSX-Datei auswählen.")
        with self._lock:
            self._state = WatchState(file_path=str(resolved))
            self._save_state()
        return self.check_once()

    def clear(self) -> None:
        with self._lock:
            self._state = WatchState()
            self._save_state()

    def check_once(self) -> bool:
        with self._lock:
            watched_path = Path(self._state.file_path) if self._state.file_path else None
            previous_signature = (self._state.modified_ns, self._state.size)
        if watched_path is None:
            return False
        try:
            stat = watched_path.stat()
            signature = (stat.st_mtime_ns, stat.st_size)
            if signature == previous_signature:
                return False
            payload = watched_path.read_bytes()
            engine = create_database_engine(self.settings)
            try:
                with Session(engine) as session:
                    if watched_path.suffix.lower() == ".xlsx":
                        result = import_xlsx_bytes(session, watched_path.name, payload)
                    else:
                        result = import_csv_text(
                            session,
                            watched_path.name,
                            payload.decode("utf-8-sig"),
                        )
            finally:
                engine.dispose()
            if result.status == "failed":
                raise ValueError("Die überwachte Datei enthält keine importierbaren Werte.")
        except (OSError, UnicodeDecodeError, ValueError, KeyError, SQLAlchemyError) as error:
            with self._lock:
                self._state.last_error = str(error)
                self._save_state()
            self._logger.warning("watched_file_import_failed", error=str(error))
            return False
        with self._lock:
            self._state.modified_ns, self._state.size = signature
            self._state.last_imported_at = datetime.now(UTC).isoformat()
            self._state.last_error = ""
            self._save_state()
        self._logger.info(
            "watched_file_imported",
            file_name=watched_path.name,
            imported_rows=result.imported_rows,
            failed_rows=result.failed_rows,
        )
        return True

    def start(self) -> None:
        if self._thread is not None:
            return
        self._thread = threading.Thread(
            target=self._run,
            name="performance-cockpit-file-watch",
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=max(self.interval_seconds, 1))
            self._thread = None

    def _run(self) -> None:
        self.check_once()
        while not self._stop_event.wait(self.interval_seconds):
            self.check_once()


def select_report_file() -> Path | None:
    from tkinter import Tk, filedialog

    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    try:
        selected = filedialog.askopenfilename(
            title="Performance-Report automatisch überwachen",
            filetypes=[
                ("Performance-Reports", "*.xlsx *.csv"),
                ("Excel-Arbeitsmappe", "*.xlsx"),
                ("CSV-Datei", "*.csv"),
            ],
        )
    finally:
        root.destroy()
    return Path(selected) if selected else None
