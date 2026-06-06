from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_returns_app_name():
    response = client.get("/api/v1/")
    assert response.status_code == 200
    data = response.json()
    assert data["app"] == "SnappCart API"
    assert "docs" in data


def test_health_endpoint_returns_status():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "services" in data
    assert "api" in data["services"]