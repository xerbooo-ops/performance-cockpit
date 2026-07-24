from fastapi.testclient import TestClient


def test_health_endpoint_reports_service_status(client: TestClient) -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "performance-cockpit-api",
        "version": "1.0.4",
    }
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"


def test_local_diagnostics(client: TestClient) -> None:
    response = client.get("/api/v1/system/diagnostics")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "version": "1.0.4",
        "database": "ready",
        "local_only": True,
        "metrics": 0,
        "measurements": 0,
        "imports": 0,
    }
