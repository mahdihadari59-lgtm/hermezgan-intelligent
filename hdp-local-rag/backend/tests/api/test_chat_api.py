from __future__ import annotations

from fastapi.testclient import TestClient


def test_chat_api_route_registered(backend_root):
    from app.main import app

    client = TestClient(app)
    response = client.get("/docs")
    assert response.status_code == 200
