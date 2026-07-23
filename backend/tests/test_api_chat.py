# ============================================================
# test_api_chat.py - تست‌های API چت‌بات
# ============================================================
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestChatAPI:
    """تست‌های API چت‌بات"""

    def test_health_check(self):
        """تست سلامت سرویس"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_root_endpoint(self):
        """تست ریشه API"""
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()

    def test_chat_message_endpoint(self):
        """تست ارسال پیام به چت‌بات"""
        response = client.post(
            "/api/v1/chat/message",
            json={
                "message": "سلام",
                "user_id": "test_user",
                "latitude": 27.2158,
                "longitude": 56.2808
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "intent" in data
        assert "confidence" in data

    def test_chat_history_endpoint(self):
        """تست دریافت تاریخچه چت"""
        response = client.get("/api/v1/chat/history/test_user")
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "messages" in data

    def test_invalid_message(self):
        """تست پیام خالی"""
        response = client.post(
            "/api/v1/chat/message",
            json={
                "message": "",
                "user_id": "test_user"
            }
        )
        # FastAPI اعتبارسنجی می‌کند و 422 برمی‌گرداند
        assert response.status_code == 422

    def test_chat_without_location(self):
        """تست چت بدون موقعیت مکانی"""
        response = client.post(
            "/api/v1/chat/message",
            json={
                "message": "نزدیک‌ترین بیمارستان",
                "user_id": "test_user"
            }
        )
        # بدون موقعیت، پاسخ با موفقیت برمی‌گردد اما پیشنهاد اشتراک موقعیت می‌دهد
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        # باید پیشنهاد اشتراک موقعیت باشد
        assert any("موقعیت" in s for s in data.get("suggestions", []))

    def test_chat_stats(self):
        """تست آمار چت"""
        response = client.get("/api/v1/chat/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_messages" in data
        assert "avg_processing_time" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
