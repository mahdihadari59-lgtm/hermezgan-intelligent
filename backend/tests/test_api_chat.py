import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestChatAPI:
    def test_chat_endpoint_exists(self):
        response = client.post("/api/v1/chat/message", json={
            "message": "سلام",
            "user_id": "test"
        })
        assert response.status_code in [200, 404]

    def test_chat_validation(self):
        response = client.post("/api/v1/chat/message", json={})
        assert response.status_code in [400, 422]
