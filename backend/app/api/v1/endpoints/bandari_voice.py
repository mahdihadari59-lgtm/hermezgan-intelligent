# ============================================================
# bandari_voice.py - تشخیص گفتار (Vosk) + پردازش گویش بندری
# ============================================================
from __future__ import annotations

import os
import json
import logging
import tempfile
import wave

from fastapi import APIRouter, HTTPException, UploadFile, File

from app.providers.bandari_provider import BandariProvider

logger = logging.getLogger(__name__)

router = APIRouter()

BANDARI_ENGINE_URL = os.getenv("BANDARI_ENGINE_URL", "http://127.0.0.1:5200")
_bandari_provider = BandariProvider(base_url=BANDARI_ENGINE_URL)


def _transcribe_wav(content: bytes) -> dict:
    """تبدیل فایل صوتی WAV به متن با Vosk"""
    try:
        from vosk import Model, KaldiRecognizer
    except ImportError:
        return {
            "success": False,
            "text": "",
            "error": "vosk نصب نیست",
            "install": "pip install vosk",
        }

    model_path = os.path.expanduser("~/.local/share/vosk-model-fa")
    if not os.path.exists(model_path):
        return {
            "success": False,
            "text": "",
            "error": "مدل Vosk فارسی یافت نشد",
            "install_model": (
                "wget https://alphacephei.com/vosk/models/vosk-model-small-fa-0.42.zip "
                "&& unzip vosk-model-small-fa-0.42.zip -d ~/.local/share/vosk-model-fa"
            ),
        }

    model = Model(model_path)
    recognizer = KaldiRecognizer(model, 16000)

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        wf = wave.open(tmp_path, "rb")
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
            return {"success": False, "text": "", "error": "فایل صوتی باید mono PCM باشد"}

        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            recognizer.AcceptWaveform(data)

        result = json.loads(recognizer.FinalResult())
        return {
            "success": True,
            "text": result.get("text", ""),
            "confidence": result.get("confidence", 0),
            "provider": "vosk",
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
            "confidence": stt_result.get("confidence", 0),
            "dialect": detect_result,
            "translation": translate_result,
        }
    except Exception as e:
        logger.error(f"خطا در transcribe-and-process: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def status():
    """وضعیت سرویس Vosk + Bandari Engine"""
    vosk_ok = False
    model_ok = False
    try:
        import vosk  # noqa: F401
        vosk_ok = True
        model_path = os.path.expanduser("~/.local/share/vosk-model-fa")
        model_ok = os.path.exists(model_path)
    except ImportError:
        pass

    return {
        "status": "active",
        "vosk_installed": vosk_ok,
        "fa_model_available": model_ok,
        "bandari_engine_url": BANDARI_ENGINE_URL,
    }
