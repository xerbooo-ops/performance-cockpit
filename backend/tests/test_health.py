from fastapi.testclient import TestClient

from performance_cockpit.config import Settings
from performance_cockpit.main import create_app


def test_health_endpoint_reports_service_status() -> None:
    app = create_app(Settings(_env_file=None))

    with TestClient(app) as client:
        response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "performance-cockpit-api",
        "version": "0.2.0",
    }
