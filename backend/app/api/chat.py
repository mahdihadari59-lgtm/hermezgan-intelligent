from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.orchestrator_service import OrchestratorService

router = APIRouter()
_service = OrchestratorService()

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
    return await _service.health()

def _payload(req: ChatRequest) -> Dict[str, Any]:
    payload = req.model_dump()
    payload["query"] = req.query or req.message or req.text
    payload["conversationId"] = req.conversationId or req.conversation_id
    payload["userId"] = req.userId or req.user_id
    return payload

@router.post("/chat")
async def chat(req: ChatRequest):
    try:
        payload = _payload(req)
        if not payload.get("query"):
            raise HTTPException(status_code=400, detail="query/message/text required")
        return await _service.chat(payload)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ask")
async def ask(req: ChatRequest):
    return await chat(req)
