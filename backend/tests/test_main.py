import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "هرمزگان هوشمند" in response.json()["message"]

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_ping():
    response = client.get("/api/v1/ping")
    assert response.status_code == 200
    assert response.json()["status"] == "pong"
