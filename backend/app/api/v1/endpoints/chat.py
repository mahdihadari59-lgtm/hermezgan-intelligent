from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.chat_service import get_chat_service

router = APIRouter(tags=["Chat"])


class ChatRequest(BaseModel):
    query: str | None = None
    message: str | None = None
    text: str | None = None

    conversationId: str | None = None
    conversation_id: str | None = None

    userId: str | None = None
    user_id: str | None = None

    location: Dict[str, Any] = Field(default_factory=dict)
    dialect: str | None = None
    mode: str = "text"
    metadata: Dict[str, Any] = Field(default_factory=dict)


def _text(req: ChatRequest) -> str:
    return (req.query or req.message or req.text or "").strip()


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "ChatService",
        "provider": "BandariProvider",
    }


@router.post("/chat/message")
async def message(req: ChatRequest):
    text = _text(req)

    if not text:
        return {
            "success": False,
            "response": "query/message/text required",
            "intent": "general",
            "confidence": 0.0,
            "source": "validation",
            "dialect": {},
            "suggestions": [],
        }

    user_id = req.userId or req.user_id or "anonymous"
    session_id = req.conversationId or req.conversation_id

    service = get_chat_service()

    result = await service.process_message(
        text,
        user_id,
        session_id=session_id,
        latitude=req.location.get("latitude") if req.location else None,
        longitude=req.location.get("longitude") if req.location else None,
    )

    return result


@router.post("/chat/ask")
async def ask(req: ChatRequest):
    return await message(req)
