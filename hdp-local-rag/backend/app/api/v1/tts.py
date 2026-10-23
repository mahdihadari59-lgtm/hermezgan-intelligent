# ============================================================
# tts.py - تبدیل متن به گفتار عمومی (provider-agnostic)
# ============================================================
import logging
import os

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()


class TTSRequest(BaseModel):
    text: str
    language: str = "fa"
    speed: float = 1.0


@router.post("/speak")
async def speak(payload: TTSRequest):
    """تبدیل متن به گفتار با سرویس عمومی"""
    try:
        from app.services.tts_service import get_tts_service

        service = get_tts_service()
        result = await service.synthesize(payload.text, payload.language, speed=payload.speed)
        return result
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/voices")
async def list_voices():
    """لیست صداهای موجود"""
    return {
        "success": True,
        "voices": [
            {"id": "default", "name": "Default"},
            {"id": "neutral", "name": "Neutral"},
            {"id": "clear", "name": "Clear"},
        ],
    }


@router.get("/status")
async def tts_status():
    """وضعیت سرویس تبدیل متن به گفتار"""
    api_key = os.getenv("TTS_API_KEY") or os.getenv("ELEVENLABS_API_KEY", "")
    voice_id = os.getenv("TTS_VOICE_ID") or os.getenv("ELEVENLABS_VOICE_ID", "")
    provider = os.getenv("TTS_PROVIDER") or os.getenv("ELEVENLABS_PROVIDER", "generic")
    return {
        "status": "active",
        "service": "tts_service",
        "provider": provider,
        "api_key_configured": bool(api_key),
        "voice_id_configured": bool(voice_id),
        "voices_available": bool(api_key and voice_id),
    }
