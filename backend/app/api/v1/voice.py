# ============================================================
# voice.py - سرویس تشخیص گفتار (Vosk)
# ============================================================
import os
import io
import base64
import logging
import tempfile
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional

logger = logging.getLogger(__name__)
router = APIRouter()


class VoiceTextRequest(BaseModel):
    audio_base64: str
    language: Optional[str] = "fa"


@router.post("/recognize")
async def recognize_voice(file: UploadFile = File(...)):
    """تشخیص گفتار از فایل صوتی"""
    try:
        # تلاش برای vosk
        try:
            from vosk import Model, KaldiRecognizer
            import wave
            import json

            # بررسی مدل فارسی
            model_path = os.path.expanduser("~/.local/share/vosk-model-fa")
            if not os.path.exists(model_path):
                return {
                    "success": False,
                    "text": "",
                    "error": "مدل Vosk فارسی یافت نشد",
                    "install_model": "wget https://alphacephei.com/vosk/models/vosk-model-small-fa-0.42.zip && unzip vosk-model-small-fa-0.42.zip -d ~/.local/share/vosk-model-fa"
                }

            model = Model(model_path)
            recognizer = KaldiRecognizer(model, 16000)

            content = await file.read()
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp.write(content)
                tmp_path = tmp.name

            wf = wave.open(tmp_path, "rb")
            if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
                return {"success": False, "error": "فایل صوتی باید mono PCM باشد"}

            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                recognizer.AcceptWaveform(data)

            result = json.loads(recognizer.FinalResult())
            os.unlink(tmp_path)

            return {
                "success": True,
                "text": result.get("text", ""),
                "confidence": result.get("confidence", 0),
                "provider": "vosk"
            }

        except ImportError:
            return {
                "success": False,
                "error": "vosk نصب نیست",
                "install": "pip install vosk",
                "fallback": "لطفاً از تایپ متن استفاده کنید"
            }

    except Exception as e:
        logger.error(f"Voice recognition error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/text")
async def voice_from_text(request: VoiceTextRequest):
    """تبدیل متن به گفتار (برگرداندن لینک TTS)"""
    return {
        "success": True,
        "message": "برای تبدیل متن به گفتار از TTS استفاده کنید",
        "tts_endpoint": "/api/v1/tts/speak",
        "text": request.audio_base64  # در واقعیت باید decode شود
    }


@router.get("/status")
async def voice_status():
    """وضعیت سرویس Voice"""
    vosk_ok = False
    model_ok = False
    try:
        import vosk
        vosk_ok = True
        model_path = os.path.expanduser("~/.local/share/vosk-model-fa")
        model_ok = os.path.exists(model_path)
    except ImportError:
        pass

    return {
        "status": "active",
        "service": "voice_recognition",
        "provider": "vosk",
        "vosk_installed": vosk_ok,
        "fa_model_available": model_ok,
        "install": "pip install vosk && wget https://alphacephei.com/vosk/models/vosk-model-small-fa-0.42.zip"
    }
