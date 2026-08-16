# ============================================================
# copilot.py - اندپوینت واقعی Copilot Gateway
# ============================================================
from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.gateway.copilot_gateway import CopilotGateway

logger = logging.getLogger(__name__)

router = APIRouter()

_gateway: CopilotGateway | None = None


def get_copilot_gateway() -> CopilotGateway:
    global _gateway
    if _gateway is None:
        _gateway = CopilotGateway()
    return _gateway


class CopilotMessageRequest(BaseModel):
    text: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None


@router.post("/message")
async def copilot_message(payload: CopilotMessageRequest):
    """پردازش پیام از طریق Copilot Gateway (Bandari + Knowledge/Graph/Vector search pipeline)"""
    gateway = get_copilot_gateway()
    try:
        result = await gateway.handle_message(
            text=payload.text,
            session_id=payload.session_id,
            user_id=payload.user_id,
        )
        return result
    except Exception as e:
        logger.error(f"خطا در copilot gateway: {e}")
        raise HTTPException(status_code=500, detail=f"خطای داخلی copilot gateway: {e}")
