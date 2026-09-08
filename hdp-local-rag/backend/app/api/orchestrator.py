# ============================================================
# orchestrator.py - اندپوینت واقعی Orchestrator (V3)
# ============================================================
from __future__ import annotations

import json
import logging
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.services.orchestrator_service import OrchestratorService

logger = logging.getLogger(__name__)

router = APIRouter()

_service: OrchestratorService | None = None


def get_orchestrator_service() -> OrchestratorService:
    global _service
    if _service is None:
        _service = OrchestratorService()
    return _service


class ChatRequest(BaseModel):
    query: str | None = None
    text: str | None = None
    message: str | None = None
    conversationId: str | None = None
    userId: str | None = None
    location: Dict[str, Any] | None = None
    dialect: str | None = None
    mode: str = "text"
    metadata: Dict[str, Any] | None = None


@router.post("/chat")
async def orchestrator_chat(payload: ChatRequest):
    """پردازش پیام از طریق Orchestrator مرکزی (V3)"""
    service = get_orchestrator_service()
    try:
        result = await service.chat(payload.model_dump(exclude_none=True))
        return result
    except Exception as e:
        logger.error(f"خطا در orchestrator chat: {e}")
        raise HTTPException(status_code=500, detail=f"خطای داخلی orchestrator: {e}")


@router.get("/health")
async def orchestrator_health():
    """وضعیت سلامت Orchestrator و سرویس‌های زیرمجموعه"""
    service = get_orchestrator_service()
    try:
        return await service.health()
    except Exception as e:
        logger.error(f"خطا در orchestrator health: {e}")
        raise HTTPException(status_code=500, detail=f"خطای داخلی orchestrator: {e}")


@router.post("/stream")
async def orchestrator_stream(payload: ChatRequest):
    """پاسخ استریم (Server-Sent Events) از Orchestrator"""
    service = get_orchestrator_service()

    async def event_generator():
        try:
            async for item in service.stream_chat(payload.model_dump(exclude_none=True)):
                yield f"data: {json.dumps(item, ensure_ascii=False)}\n\n"
        except NotImplementedError:
            yield f"data: {json.dumps({'error': 'استریم در این نسخه orchestrator پشتیبانی نمی‌شود'}, ensure_ascii=False)}\n\n"
        except Exception as e:
            logger.error(f"خطا در orchestrator stream: {e}")
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
