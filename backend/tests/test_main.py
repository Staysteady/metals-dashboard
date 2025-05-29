from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Metals Dashboard API"
    assert data["version"] == "1.0.0"
    assert data["phase"] == "3"
    assert "endpoints" in data
    assert "health" in data["endpoints"]
    assert "prices" in data["endpoints"]


def test_ping():
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
