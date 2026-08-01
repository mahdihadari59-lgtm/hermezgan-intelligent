from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.orchestrator_v2 import HDPOrchestratorV2

router = APIRouter()
_orchestrator = HDPOrchestratorV2()

class OrchestratorRequest(BaseModel):
    query: str = Field(..., min_length=1)
    conversationId: str | None = None
    userId: str | None = None
    location: Dict[str, Any] = Field(default_factory=dict)
    dialect: str | None = None
    mode: str = "text"
    metadata: Dict[str, Any] = Field(default_factory=dict)

@router.get("/health")
async def health():
    return await _orchestrator.health()

@router.post("/chat")
async def chat(req: OrchestratorRequest):
    try:
        return await _orchestrator.handle(req.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ask")
async def ask(req: OrchestratorRequest):
    try:
        return await _orchestrator.handle(req.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
