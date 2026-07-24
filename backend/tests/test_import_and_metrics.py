from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from performance_cockpit.models import Measurement

VALID_CSV = "\n".join(
    [
        "metric_key,metric_name,description,unit,aggregation,organizational_unit,"
        "period_start,period_end,value,target_value",
        "handled_cases,Bearbeitete Vorgänge,Abgeschlossene Vorgänge,Anzahl,sum,"
        "Service Nord,2026-07-01,2026-07-07,110,100",
        "handled_cases,Bearbeitete Vorgänge,Abgeschlossene Vorgänge,Anzahl,sum,"
        "Service Nord,2026-07-08,2026-07-14,95,100",
        "quality_rate,Qualitätsquote,Positiv bewertete Vorgänge,Prozent,average,"
        "Service Nord,2026-07-01,2026-07-07,92.5,90",
        "",
    ]
)


def test_csv_import_exposes_metrics_and_summary(client: TestClient) -> None:
    response = client.post(
        "/api/v1/imports/csv",
        files={"file": ("sample.csv", VALID_CSV, "text/csv")},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    assert response.json()["imported_rows"] == 3

    metrics = client.get("/api/v1/metrics")
    assert [metric["key"] for metric in metrics.json()] == ["handled_cases", "quality_rate"]

    summary = client.get(
        "/api/v1/metrics/handled_cases/summary",
        params={"organizational_unit": "Service Nord"},
    )
    assert summary.status_code == 200
    assert summary.json() == {
        "metric_key": "handled_cases",
        "display_name": "Bearbeitete Vorgänge",
        "organizational_unit": "Service Nord",
        "period_start": "2026-07-01",
        "period_end": "2026-07-14",
        "unit": "Anzahl",
        "aggregation": "sum",
        "value": "205.00",
        "target_value": "200.00",
        "deviation": "5.00",
        "attainment_percent": "102.50",
        "measurement_count": 2,
    }


def test_reimport_updates_existing_measurement(client: TestClient, session: Session) -> None:
    client.post("/api/v1/imports/csv", files={"file": ("first.csv", VALID_CSV, "text/csv")})
    updated = VALID_CSV.replace(",110,100", ",120,100")

    response = client.post(
        "/api/v1/imports/csv",
        files={"file": ("updated.csv", updated, "text/csv")},
    )

    assert response.status_code == 200
    measurements = session.query(Measurement).all()
    assert len(measurements) == 3
    assert measurements[0].value == Decimal("120")


def test_csv_import_returns_row_level_validation_errors(client: TestClient) -> None:
    invalid_csv = VALID_CSV + (
        "bad key,Ungültig,Fehler,Anzahl,sum,Service Nord,2026-07-14,2026-07-01,10,20\n"
    )

    response = client.post(
        "/api/v1/imports/csv",
        files={"file": ("invalid.csv", invalid_csv, "text/csv")},
    )

    body = response.json()
    assert response.status_code == 200
    assert body["status"] == "completed_with_errors"
    assert body["imported_rows"] == 3
    assert body["failed_rows"] == 1
    assert body["errors"][0]["row"] == 5


def test_csv_import_accepts_empty_optional_target(client: TestClient) -> None:
    csv_without_target = VALID_CSV.replace("92.5,90", "92.5,")

    response = client.post(
        "/api/v1/imports/csv",
        files={"file": ("without-target.csv", csv_without_target, "text/csv")},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "completed"


def test_missing_metric_and_invalid_upload_return_clear_errors(client: TestClient) -> None:
    metric_response = client.get(
        "/api/v1/metrics/unknown/summary",
        params={"organizational_unit": "Service Nord"},
    )
    upload_response = client.post(
        "/api/v1/imports/csv",
        files={"file": ("metrics.txt", "not csv", "text/plain")},
    )

    assert metric_response.status_code == 404
    assert upload_response.status_code == 415
