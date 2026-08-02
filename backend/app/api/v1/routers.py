from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
import tempfile
import os

from .health import router as health_router
from .ping import router as ping_router
from .auth import router as auth_router
from .endpoints.chat import router as chat_router
from .endpoints.voice import router as voice_router
from .endpoints.locations import router as locations_router
from .analytics import router as analytics_router
from .traffic import router as traffic_router
from .tourism import router as tourism_router
from .hospitals import router as hospitals_router
from .fuel import router as fuel_router
from .weather import router as weather_router
from .emergency import router as emergency_router
from .municipality import router as municipality_router
from .ai import router as ai_router
from .bandari import router as bandari_router
from .search import router as search_router

from app.core.speech_to_text import get_speech_engine
from app.services.chat_service import ChatService

router = APIRouter()

for sub_router in (
    health_router,
    ping_router,
    auth_router,
    chat_router,
    voice_router,
    locations_router,
    analytics_router,
    traffic_router,
    tourism_router,
    hospitals_router,
    fuel_router,
    weather_router,
    emergency_router,
    municipality_router,
    ai_router,
    bandari_router,
    search_router,
):
    router.include_router(sub_router)


@router.get("/speech/status")
async def speech_status():
    stt = get_speech_engine()
    return {
        "status": "active",
        "layers": {
            "layer1_vosk": stt.health_check(),
            "layer2_bandari": {"url": "http://127.0.0.1:5200", "status": "active"},
            "layer3_rag": {"status": "active", "db": "hdp_v2.db (1.2GB)"},
            "layer4_ai": {"status": "active", "service": "ChatService"}
        }
    }


@router.post("/speech/process")
async def process_speech_with_ai(
    audio: UploadFile = File(...),
    user_id: str = Form("speech_user"),
    language: str = Form("fa")
):
    try:
        audio_bytes = await audio.read()
        if not audio_bytes:
            return JSONResponse(400, {"success": False, "error": "فایل خالی است"})

        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
            tmp.write(audio_bytes)
            audio_path = tmp.name

        try:
            stt = get_speech_engine()
            stt_result = stt.transcribe(audio_path)
            os.unlink(audio_path)

            if not stt_result.get("success"):
                return {"success": False, "error": stt_result.get("error")}

            text = stt_result.get("text", "").strip()
            if not text:
                return {"success": False, "error": "No speech detected"}

            chat_service = ChatService()
            chat_result = chat_service.process_message(text, user_id)

            return {
                "success": True,
                "layers": {
                    "layer1_vosk": {"text": text, "confidence": stt_result.get("confidence", 0.0)},
                    "layer4_ai": {"response": (chat_result.get("response") or "")[:100] + "..."}
                },
                "response": chat_result.get("response"),
                "intent": chat_result.get("intent"),
                "confidence": chat_result.get("confidence"),
                "suggestions": chat_result.get("suggestions", [])
            }

        except Exception as e:
            try:
                os.unlink(audio_path)
            except:
                pass
            return JSONResponse(500, {"success": False, "error": str(e)})

    except Exception as e:
        return JSONResponse(500, {"success": False, "error": str(e)})


# سازگاری با کدهای قدیمی که api_router رو مستقیم import می‌کنن
api_router = router
