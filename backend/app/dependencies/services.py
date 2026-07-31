from __future__ import annotations

import importlib
from functools import lru_cache

from app.config import HDP_KNOWLEDGE_DB_PATH
from app.gateway.copilot_gateway import CopilotGateway
from app.services.chat_service import ChatService


def _lazy_service(module_path: str, class_name: str):
    module = importlib.import_module(module_path)
    cls = getattr(module, class_name)
    return cls()


@lru_cache(maxsize=1)
def get_copilot_gateway() -> CopilotGateway:
    return CopilotGateway(db_path=str(HDP_KNOWLEDGE_DB_PATH))


@lru_cache(maxsize=1)
def get_chat_service() -> ChatService:
    return ChatService()


@lru_cache(maxsize=1)
def get_location_service():
    return _lazy_service("app.services.location_service", "LocationService")


@lru_cache(maxsize=1)
def get_camera_service():
    return _lazy_service("app.services.camera_service", "CameraService")


@lru_cache(maxsize=1)
def get_hotspot_service():
    return _lazy_service("app.services.hotspot_service", "HotspotService")


@lru_cache(maxsize=1)
def get_auth_service():
    return _lazy_service("app.services.auth_service", "AuthService")


@lru_cache(maxsize=1)
def get_user_service():
    return _lazy_service("app.services.user_service", "UserService")


@lru_cache(maxsize=1)
def get_analytics_service():
    return _lazy_service("app.services.analytics_service", "AnalyticsService")


@lru_cache(maxsize=1)
def get_nlp_service():
    return _lazy_service("app.services.nlp_service", "NlpService")


@lru_cache(maxsize=1)
def get_websocket_service():
    return _lazy_service("app.services.websocket_service", "WebsocketService")


@lru_cache(maxsize=1)
def get_file_service():
    return _lazy_service("app.services.file_service", "FileService")


@lru_cache(maxsize=1)
def get_email_service():
    return _lazy_service("app.services.email_service", "EmailService")
