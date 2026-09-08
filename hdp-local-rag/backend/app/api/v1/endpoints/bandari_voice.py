# ============================================================
# bandari_voice.py - تشخیص گفتار (Vosk via Node bridge) + پردازش گویش بندری
# ============================================================
from __future__ import annotations

import os
import logging
import tempfile

from fastapi import APIRouter, HTTPException, UploadFile, File

from app.providers.bandari_provider import BandariProvider
from app.core.speech_to_text import get_speech_engine

logger = logging.getLogger(__name__)

router = APIRouter()

BANDARI_ENGINE_URL = os.getenv("BANDARI_ENGINE_URL", "http://127.0.0.1:5200")
_bandari_provider = BandariProvider(base_url=BANDARI_ENGINE_URL)
_stt = get_speech_engine()


def _transcribe_wav(content: bytes) -> dict:
    """تبدیل فایل صوتی WAV به متن با Vosk (از طریق Node bridge)"""
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        result = _stt.transcribe(tmp_path)
        if not result.get("success"):
            return {"success": False, "text": "", "error": result.get("error", "خطای نامشخص در STT")}

        return {
            "success": True,
            "text": result.get("text", ""),
            "provider": "vosk-node-bridge",
        }
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


@router.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    """تبدیل گفتار به متن (فقط Vosk، بدون پردازش بندری)"""
    try:
        content = await file.read()
        return _transcribe_wav(content)
    except Exception as e:
        logger.error(f"خطا در transcribe: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transcribe-and-process")
async def transcribe_and_process(file: UploadFile = File(...)):
    """تبدیل گفتار به متن + تشخیص لهجه + ترجمه به فارسی معیار"""
    try:
        content = await file.read()
        stt_result = _transcribe_wav(content)

        if not stt_result.get("success"):
            return stt_result

        text = stt_result.get("text", "").strip()
        if not text:
            return {"success": False, "text": "", "error": "صدایی تشخیص داده نشد"}

        try:
            detect_result = await _bandari_provider.detect(text)
        except Exception as e:
            logger.warning(f"خطا در تشخیص لهجه: {e}")
            detect_result = None

        try:
            translate_result = await _bandari_provider.translate(text)
        except Exception as e:
            logger.warning(f"خطا در ترجمه: {e}")
            translate_result = None

        return {
            "success": True,
            "text": text,
            "dialect": detect_result,
            "translation": translate_result,
        }
    except Exception as e:
        logger.error(f"خطا در transcribe-and-process: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def status():
    """وضعیت سرویس Vosk (Node bridge) + Bandari Engine"""
    health = _stt.health_check()
    return {
        "status": "active",
        "vosk_installed": health["stt_cli_exists"],
        "fa_model_available": health["model_exists"],
        "model_path": health["model_path"],
        "bandari_engine_url": BANDARI_ENGINE_URL,
    }
