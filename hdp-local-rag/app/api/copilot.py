from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.copilot_service import CopilotService

router = APIRouter()
_service = CopilotService()

class CopilotChatRequest(BaseModel):
    query: str = Field(..., min_length=1)
    context: Dict[str, Any] = Field(default_factory=dict)

@router.get("/health")
async def health():
    return await _service.health()

@router.post("/ask")
async def ask(req: CopilotChatRequest):
    try:
        return await _service.ask(req.query, req.context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat")
async def chat(req: CopilotChatRequest):
    try:
        return await _service.ask(req.query, req.context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sources")
async def sources(q: str, limit: int = 5):
    try:
        result = _service.hybrid.search(q, limit=limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
