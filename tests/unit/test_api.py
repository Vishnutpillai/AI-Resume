from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Intelligent Resume Job Matcher API"
    assert data["version"] == "1.0.0"


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert "service" in data
    assert "environment" in data


def test_api_root_endpoint():
    response = client.get("/api/v1/")

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Intelligent Resume Job Matcher API"
    assert data["version"] == "1.0.0"