from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest


BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


@pytest.fixture(scope="session")
def backend_root() -> Path:
    return BACKEND_ROOT


@pytest.fixture(scope="session")
def db_path() -> Path:
    from app.config import HDP_KNOWLEDGE_DB_PATH
    return Path(os.getenv("HDP_KNOWLEDGE_DB_PATH", str(HDP_KNOWLEDGE_DB_PATH))).expanduser().resolve()


@pytest.fixture()
def chat_service():
    from app.services.chat_service import ChatService
    return ChatService()


@pytest.fixture()
def gateway():
    from app.gateway.copilot_gateway import CopilotGateway
    from app.config import HDP_KNOWLEDGE_DB_PATH
    return CopilotGateway(db_path=str(HDP_KNOWLEDGE_DB_PATH))
