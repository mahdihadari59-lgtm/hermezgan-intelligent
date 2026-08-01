from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
import tempfile
import os

from .ping import router as ping_router
from .endpoints.chat import router as chat_router
from .endpoints.voice import router as voice_router
from .endpoints.locations import router as locations_router

from app.core.speech_to_text import get_speech_engine
from app.services.chat_service import ChatService

router = APIRouter()

router.include_router(ping_router)
router.include_router(chat_router)
router.include_router(voice_router)
router.include_router(locations_router)


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
            # لایه ۱: Vosk STT
            stt = get_speech_engine()
            stt_result = stt.transcribe(audio_path)
            os.unlink(audio_path)
            
            if not stt_result.get("success"):
                return {"success": False, "error": stt_result.get("error")}
            
            text = stt_result.get("text", "").strip()
            if not text:
                return {"success": False, "error": "No speech detected"}
            
            # لایه ۲: Bandari + لایه ۳: RAG + لایه ۴: AI
            chat_service = ChatService()
            chat_result = await chat_service.process_message(
                message=text,
                user_id=user_id,
                language=language
            )
            
            return {
                "success": True,
                "layers": {
                    "layer1_vosk": {"text": text, "confidence": stt_result.get("confidence", 0.0)},
                    "layer2_bandari": {"normalized": chat_result.get("normalized_text", text), "dialect": chat_result.get("dialect", "standard")},
                    "layer3_rag": {"source": chat_result.get("source", "database")},
                    "layer4_ai": {"response": chat_result.get("response")[:100] + "..."}
                },
                "response": chat_result.get("response"),
                "intent": chat_result.get("intent"),
                "source": chat_result.get("source"),
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
