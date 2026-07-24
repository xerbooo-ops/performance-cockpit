from io import BytesIO

from fastapi.testclient import TestClient
from openpyxl import Workbook


def test_python_dashboard_renders_without_frontend_build(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "Performance Cockpit" in response.text
    assert "Python-only" in response.text
    assert "TypeScript" in response.text
    assert 'action="/web/import"' in response.text


def test_python_dashboard_imports_and_filters_by_epa(client: TestClient) -> None:
    workbook = Workbook()
    sheet = workbook.active
    headers = ["Teamleiter", "Mitarbeiter", "EPA", "VVL", "BNT", "Calls"]
    for column, header in enumerate(headers, start=2):
        sheet.cell(11, column, header)
    for column, value in enumerate(["Leitung", "Name", "EPA-7", 2, 1, 5], start=2):
        sheet.cell(12, column, value)
    payload = BytesIO()
    workbook.save(payload)

    imported = client.post(
        "/web/import",
        files={
            "file": (
                "report.xlsx",
                payload.getvalue(),
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
        follow_redirects=True,
    )

    assert imported.status_code == 200
    assert "6 Zeilen importiert" in imported.text
    assert "EPA-7" in imported.text
    assert "Potsdam" in imported.text
    assert "Leitung" not in imported.text
    assert ">Name<" not in imported.text


def test_python_dashboard_reset_requires_delete(client: TestClient) -> None:
    rejected = client.post(
        "/web/reset",
        data={"confirmation": "delete"},
        follow_redirects=True,
    )
    accepted = client.post(
        "/web/reset",
        data={"confirmation": "DELETE"},
        follow_redirects=True,
    )

    assert "Bestätigung war nicht DELETE" in rejected.text
    assert "Alle lokalen Daten wurden gelöscht" in accepted.text
