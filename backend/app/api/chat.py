from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.chat_service import get_chat_service

router = APIRouter()

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

@router.get("/health")
async def health():
    return {"status": "ok", "service": "ChatService (CopilotGateway)"}

def _query_of(req: ChatRequest) -> str:
    return req.query or req.message or req.text or ""

@router.post("/chat")
async def chat(req: ChatRequest):
    query = _query_of(req)
    if not query:
        raise HTTPException(status_code=400, detail="query/message/text required")

    user_id = req.userId or req.user_id or "anonymous"
    session_id = req.conversationId or req.conversation_id

    try:
        chat_service = get_chat_service()
        result = await chat_service.process_message(
            query,
            user_id,
            session_id=session_id,
            latitude=req.location.get("latitude") if req.location else None,
            longitude=req.location.get("longitude") if req.location else None,
        )
        return {
            "answer": result.get("response", ""),
            "intent": result.get("intent", "general"),
            "confidence": result.get("confidence", 0.0),
            "suggestions": result.get("suggestions", []),
            "dialect": result.get("dialect", {}),
            "success": result.get("success", True),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ask")
async def ask(req: ChatRequest):
    return await chat(req)
