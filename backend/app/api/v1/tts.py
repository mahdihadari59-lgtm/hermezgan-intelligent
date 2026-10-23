# ============================================================
# tts.py - تبدیل متن به گفتار عمومی (provider-agnostic)
# ============================================================
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class TTSRequest(BaseModel):
    text: str
    language: str = "fa"
    speed: float = 1.0


@router.post("/speak")
async def speak(payload: TTSRequest):
    """تبدیل متن به گفتار"""
    try:
        from app.services.tts_service import DefaultTTSProvider
        provider = DefaultTTSProvider()
        result = await provider.synthesize(payload.text, payload.language)
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
            {"id": "voice-1", "name": "Default"},
            {"id": "voice-2", "name": "Neutral"},
            {"id": "voice-3", "name": "Clear"},
        ]
    }


@router.get("/status")
async def tts_status():
    """وضعیت سرویس تبدیل متن به گفتار"""
    api_key = os.getenv("TTS_API_KEY", "")
    voice_id = os.getenv("TTS_VOICE_ID", "")
    provider = os.getenv("TTS_PROVIDER", "generic")
    return {
        "status": "active",
        "service": "tts_service",
        "provider": provider,
        "api_key_configured": bool(api_key),
        "voice_id_configured": bool(voice_id),
        "voices_available": bool(api_key and voice_id),
    }
