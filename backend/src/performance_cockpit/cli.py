import argparse
from pathlib import Path

from performance_cockpit.database import get_session_factory
from performance_cockpit.services.csv_import import import_csv_text


def main() -> None:
    parser = argparse.ArgumentParser(description="Import KPI measurements from a CSV file")
    parser.add_argument("csv_file", type=Path)
    args = parser.parse_args()

    content = args.csv_file.read_text(encoding="utf-8-sig")
    with get_session_factory()() as session:
        result = import_csv_text(session, args.csv_file.name, content)
    print(result.model_dump_json(indent=2))
