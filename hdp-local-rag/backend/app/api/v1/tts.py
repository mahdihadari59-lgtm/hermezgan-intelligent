# ============================================================
# tts.py - تبدیل متن به گفتار ElevenLabs
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
        from app.services.tts_service import ElevenLabsTTSProvider
        provider = ElevenLabsTTSProvider()
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
            {"id": "JBFqnCBsd6RMkjVDRZzb", "name": "Bella"},
            {"id": "AZnzlk1XvdvUeBnXmlld", "name": "Adam"},
            {"id": "EXAVITQu4vr4xnSDxMaL", "name": "Sam"}
        ]
    }


@router.get("/status")
async def tts_status():
    """وضعیت سرویس ElevenLabs TTS"""
    api_key = os.getenv("ELEVENLABS_API_KEY", "")
    voice_id = os.getenv("ELEVENLABS_VOICE_ID", "")
    return {
        "status": "active",
        "service": "elevenlabs_tts",
        "api_key_configured": bool(api_key),
        "voice_id_configured": bool(voice_id),
        "voices_available": bool(api_key and voice_id)
    }
