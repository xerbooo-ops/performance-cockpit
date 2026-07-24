import csv
import io
from datetime import date, datetime
from decimal import Decimal

from openpyxl import load_workbook
from sqlalchemy.orm import Session

from performance_cockpit.schemas import ImportResult
from performance_cockpit.services.csv_import import import_csv_text


def _cell_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return format(value, "f")
    return str(value)


def import_xlsx_bytes(session: Session, file_name: str, content: bytes) -> ImportResult:
    workbook = load_workbook(io.BytesIO(content), read_only=True, data_only=True)
    try:
        worksheet = workbook.active
        rows = worksheet.iter_rows(values_only=True)
        output = io.StringIO()
        writer = csv.writer(output, lineterminator="\n")
        for row in rows:
            writer.writerow([_cell_text(value) for value in row])
        # Both file formats intentionally share validation and idempotent persistence.
        return import_csv_text(session, file_name, output.getvalue())
    finally:
        workbook.close()
