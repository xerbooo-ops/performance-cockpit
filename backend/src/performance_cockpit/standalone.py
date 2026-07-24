import os
import socket
import sys
import threading
import webbrowser
from pathlib import Path

import uvicorn

from performance_cockpit.config import Settings
from performance_cockpit.database import initialize_database
from performance_cockpit.main import create_app


def bundled_frontend_dir() -> Path:
    bundle_path = getattr(sys, "_MEIPASS", None)
    bundle_root = Path(bundle_path) if bundle_path else Path(__file__).resolve().parents[2]
    return bundle_root / "frontend"


def bundled_migrations_dir() -> Path:
    bundle_path = getattr(sys, "_MEIPASS", None)
    bundle_root = Path(bundle_path) if bundle_path else Path(__file__).resolve().parents[2]
    return bundle_root / "migrations"


def available_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


def main() -> None:
    settings = Settings(
        _env_file=None,
        app_name="Performance Cockpit",
        environment="standalone",
        frontend_dir=bundled_frontend_dir(),
        migrations_dir=bundled_migrations_dir(),
        cors_origins=[],
    )
    initialize_database(settings)
    port = int(os.environ.get("PERFORMANCE_COCKPIT_PORT", available_port()))
    url = f"http://127.0.0.1:{port}"
    if os.environ.get("PERFORMANCE_COCKPIT_NO_BROWSER") != "1":
        threading.Timer(1.0, webbrowser.open, args=(url,)).start()
    uvicorn.run(create_app(settings), host="127.0.0.1", port=port, log_level="warning")


if __name__ == "__main__":
    main()
