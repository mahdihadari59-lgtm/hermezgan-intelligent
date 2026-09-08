#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

cd ~/hermezgan-intelligent/backend
TS="$(date +%Y%m%d_%H%M%S)"

backup() {
  local f="$1"
  if [ -f "$f" ] && [ ! -f "${f}.bak.${TS}" ]; then
    cp "$f" "${f}.bak.${TS}"
  fi
}

mkdir -p app/dependencies app/services

backup app/config.py
backup app/dependencies/services.py
backup app/dependencies/__init__.py
backup app/services/chat_service.py

cat > app/config.py <<'PY'
from __future__ import annotations

import os
from pathlib import Path

from app.core.config.settings import Settings

settings = Settings()

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_KNOWLEDGE_DB = PROJECT_ROOT / "data" / "hdp_v2.db"
HDP_KNOWLEDGE_DB_PATH = Path(
    os.getenv("HDP_KNOWLEDGE_DB_PATH", str(DEFAULT_KNOWLEDGE_DB))
).expanduser().resolve()
PY

cat > app/dependencies/services.py <<'PY'
from __future__ import annotations

from functools import lru_cache

from app.config import HDP_KNOWLEDGE_DB_PATH
from app.gateway.copilot_gateway import CopilotGateway


def _build_service(module_path: str, class_name: str):
    module = __import__(module_path, fromlist=[class_name])
    cls = getattr(module, class_name)
    return cls()


@lru_cache(maxsize=1)
def get_copilot_gateway() -> CopilotGateway:
    return CopilotGateway(db_path=str(HDP_KNOWLEDGE_DB_PATH))


@lru_cache(maxsize=1)
def get_chat_service():
    from app.services.chat_service import ChatService
    return ChatService()


@lru_cache(maxsize=1)
def get_location_service():
    return _build_service("app.services.location_service", "LocationService")


@lru_cache(maxsize=1)
def get_camera_service():
    return _build_service("app.services.camera_service", "CameraService")


@lru_cache(maxsize=1)
def get_hotspot_service():
    return _build_service("app.services.hotspot_service", "HotspotService")


@lru_cache(maxsize=1)
def get_auth_service():
    return _build_service("app.services.auth_service", "AuthService")


@lru_cache(maxsize=1)
def get_user_service():
    return _build_service("app.services.user_service", "UserService")


@lru_cache(maxsize=1)
def get_analytics_service():
    return _build_service("app.services.analytics_service", "AnalyticsService")


@lru_cache(maxsize=1)
def get_nlp_service():
    return _build_service("app.services.nlp_service", "NlpService")


@lru_cache(maxsize=1)
def get_websocket_service():
    return _build_service("app.services.websocket_service", "WebsocketService")


@lru_cache(maxsize=1)
def get_file_service():
    return _build_service("app.services.file_service", "FileService")


@lru_cache(maxsize=1)
def get_email_service():
    return _build_service("app.services.email_service", "EmailService")
PY

cat > app/dependencies/__init__.py <<'PY'
from .services import (
    get_analytics_service,
    get_auth_service,
    get_camera_service,
    get_chat_service,
    get_copilot_gateway,
    get_email_service,
    get_file_service,
    get_hotspot_service,
    get_location_service,
    get_nlp_service,
    get_user_service,
    get_websocket_service,
)

__all__ = [
    "get_analytics_service",
    "get_auth_service",
    "get_camera_service",
    "get_chat_service",
    "get_copilot_gateway",
    "get_email_service",
    "get_file_service",
    "get_hotspot_service",
    "get_location_service",
    "get_nlp_service",
    "get_user_service",
    "get_websocket_service",
]
PY

cat > app/services/chat_service.py <<'PY'
from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.config import HDP_KNOWLEDGE_DB_PATH
from app.gateway.copilot_gateway import CopilotGateway


_gateway = CopilotGateway(db_path=str(HDP_KNOWLEDGE_DB_PATH))

_DEFAULT_SUGGESTIONS = {
    "hospital": ["📞 تماس", "🧭 مسیریابی", "دیگر بیمارستان‌ها"],
    "restaurant": ["🍽️ صفحه رستوران", "⭐ نظرات", "📞 تماس"],
    "taxi": ["⏱️ زمان باقی‌مانده", "📞 تماس راننده", "❌ لغو"],
    "greeting": ["🏥 بیمارستان", "🍽️ رستوران", "🚗 تاکسی"],
    "general": ["🏥 بیمارستان", "🍽️ رستوران", "🚗 تاکسی"],
}


class ChatService:
    async def process_message(
        self,
        message: str,
        user_id: str,
        latitude: float | None = None,
        longitude: float | None = None,
        session_id: str | None = None,
    ) -> Dict[str, Any]:
        result = await _gateway.handle_message(
            text=message,
            session_id=session_id,
            user_id=user_id,
        )

        intent_data = result.get("intent") or {}
        if not isinstance(intent_data, dict):
            intent_data = {}

        knowledge = result.get("knowledge") or {}
        if not isinstance(knowledge, dict):
            knowledge = {}

        intent_name = str(
            intent_data.get("intent")
            or intent_data.get("category")
            or "general"
        ).strip().lower()

        response_text = (
            result.get("answer")
            or knowledge.get("answer")
            or result.get("response")
            or "پاسخی پیدا نشد."
        )

        confidence = intent_data.get("confidence", 1.0)
        try:
            confidence = float(confidence)
        except Exception:
            confidence = 1.0

        retrieved_documents = knowledge.get("results") or []
        if not isinstance(retrieved_documents, list):
            retrieved_documents = []

        return {
            "response": response_text,
            "intent": intent_name or "general",
            "confidence": confidence,
            "suggestions": _DEFAULT_SUGGESTIONS.get(intent_name, _DEFAULT_SUGGESTIONS["general"]),
            "retrieved_documents": retrieved_documents,
            "dialect": result.get("dialect"),
            "knowledge": knowledge,
            "session_id": session_id,
            "location": {
                "lat": latitude,
                "lng": longitude,
            } if latitude is not None and longitude is not None else None,
        }

    async def chat(
        self,
        message: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        return await _gateway.handle_message(
            text=message,
            session_id=session_id,
            user_id=user_id,
        )

    async def handle_message(
        self,
        message: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        return await self.chat(
            message,
            session_id=session_id,
            user_id=user_id,
        )


async def chat(
    message: str,
    session_id: Optional[str] = None,
    user_id: Optional[str] = None,
) -> Dict[str, Any]:
    return await _gateway.handle_message(
        text=message,
        session_id=session_id,
        user_id=user_id,
    )
PY

python3 -m py_compile \
  app/config.py \
  app/dependencies/services.py \
  app/dependencies/__init__.py \
  app/services/chat_service.py

echo "OK: patched and compiled successfully"
