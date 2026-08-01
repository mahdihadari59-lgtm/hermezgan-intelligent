"""
Speech Routes - تبدیل گفتار به متن + پردازش هوشمند
معماری: Vosk STT → Bandari Engine → Intent → RAG → AI Assistant
"""

import os
import tempfile
import logging
import base64
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from app.core.speech_to_text import get_speech_engine
from app.services.chat_service import ChatService
from app.services.voice_service import VoiceService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/speech", tags=["speech"])


class TranscribeResponse(BaseModel):
    """پاسخ تشخیص گفتار"""
    success: bool
    text: str
    normalized_text: Optional[str] = None
    dialect: Optional[str] = None
    confidence: float = 0.0
    intent: Optional[str] = None
    response: Optional[str] = None
    audio_response: Optional[str] = None  # base64
    memory_usage: Optional[dict] = None
    error: Optional[str] = None


class ChatResponseFromSpeech(BaseModel):
    """پاسخ کامل از AI Assistant"""
    success: bool
    original_text: str
    normalized_text: Optional[str] = None
    dialect: Optional[str] = None
    intent: str = "general"
    response: str
    audio_response: Optional[str] = None  # base64
    source: str = "database"
    confidence: float = 0.0
    suggestions: list[str] = []
    memory_usage: Optional[dict] = None
    error: Optional[str] = None


@router.post(
    "/transcribe",
    response_model=TranscribeResponse,
    summary="تبدیل گفتار به متن + پردازش"
)
async def transcribe_speech(
    audio: UploadFile = File(..., description="فایل صوتی (WAV, MP3, OGG)"),
    language: str = Form("fa", description="زبان (fa, en, ar)"),
    return_audio: bool = Form(False, description="بازگشت پاسخ صوتی"),
    use_bandari: bool = Form(True, description="استفاده از Bandari Engine"),
    detect_intent: bool = Form(True, description="تشخیص Intent"),
    use_rag: bool = Form(True, description="استفاده از RAG")
):
    """
    تشخیص گفتار و پردازش هوشمند
    
    زنجیره:
    Audio → Vosk STT → Bandari → Intent → RAG → AI Assistant
    """
    try:
        # ===== ۱. خواندن فایل صوتی =====
        audio_bytes = await audio.read()
        if not audio_bytes:
            raise HTTPException(status_code=400, detail="فایل صوتی خالی است")
        
        # ذخیره موقت
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
            tmp.write(audio_bytes)
            audio_path = tmp.name
        
        try:
            # ===== ۲. تبدیل گفتار به متن (Vosk STT) =====
            stt = get_speech_engine()
            stt_result = stt.transcribe(
                audio_path,
                use_bandari=use_bandari,
                return_confidence=True
            )
            
            if not stt_result.get("success", False):
                return TranscribeResponse(
                    success=False,
                    text="",
                    error=stt_result.get("error", "STT failed"),
                    memory_usage=stt_result.get("memory_usage")
                )
            
            text = stt_result.get("text", "").strip()
            normalized_text = stt_result.get("normalized_text", text)
            dialect = stt_result.get("dialect", "standard")
            confidence = stt_result.get("confidence", 0.0)
            
            if not text:
                return TranscribeResponse(
                    success=False,
                    text="",
                    error="No speech detected",
                    memory_usage=stt_result.get("memory_usage")
                )
            
            logger.info(f"🎤 STT: '{text}' (confidence: {confidence})")
            
            # ===== ۳. تشخیص Intent =====
            intent = "general"
            if detect_intent:
                intent = await detect_intent_from_text(text)
            
            # ===== ۴. دریافت پاسخ از AI Assistant (RAG) =====
            response_text = None
            audio_response = None
            
            if use_rag:
                chat_service = ChatService()
                chat_result = await chat_service.process_message(
                    message=text,
                    user_id="speech_user",
                    language=language
                )
                response_text = chat_result.get("response", "")
                intent = chat_result.get("intent", intent)
                
                # ===== ۵. تبدیل پاسخ به گفتار =====
                if return_audio and response_text:
                    voice_service = VoiceService()
                    audio_response = voice_service.text_to_speech(
                        text=response_text,
                        language=language
                    )
            
            # ===== ۶. پاسخ نهایی =====
            return TranscribeResponse(
                success=True,
                text=text,
                normalized_text=normalized_text,
                dialect=dialect,
                confidence=confidence,
                intent=intent,
                response=response_text,
                audio_response=audio_response,
                memory_usage=stt_result.get("memory_usage")
            )
            
        finally:
            # پاکسازی فایل موقت
            try:
                os.unlink(audio_path)
            except:
                pass
            
    except Exception as e:
        logger.error(f"❌ Transcribe error: {e}")
        return TranscribeResponse(
            success=False,
            text="",
            error=str(e)
        )


@router.post(
    "/process",
    response_model=ChatResponseFromSpeech,
    summary="پردازش کامل گفتار → AI Assistant"
)
async def process_speech_with_ai(
    audio: UploadFile = File(..., description="فایل صوتی"),
    user_id: str = Form("speech_user"),
    language: str = Form("fa"),
    return_audio: bool = Form(True, description="بازگشت پاسخ صوتی"),
    use_bandari: bool = Form(True)
):
    """
    پردازش کامل گفتار و دریافت پاسخ از AI Assistant
    
    زنجیره کامل:
    🎤 Audio → 🗣️ Vosk STT → 🧠 Bandari → 🎯 Intent → 📚 RAG → 🤖 AI → 🎧 Audio
    """
    try:
        # ===== ۱. خواندن فایل صوتی =====
        audio_bytes = await audio.read()
        if not audio_bytes:
            raise HTTPException(status_code=400, detail="فایل صوتی خالی است")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
            tmp.write(audio_bytes)
            audio_path = tmp.name
        
        try:
            # ===== ۲. STT =====
            stt = get_speech_engine()
            stt_result = stt.transcribe(
                audio_path,
                use_bandari=use_bandari,
                return_confidence=True
            )
            
            if not stt_result.get("success", False):
                return ChatResponseFromSpeech(
                    success=False,
                    original_text="",
                    response="",
                    error=stt_result.get("error", "STT failed")
                )
            
            original_text = stt_result.get("text", "").strip()
            normalized_text = stt_result.get("normalized_text", original_text)
            dialect = stt_result.get("dialect", "standard")
            stt_confidence = stt_result.get("confidence", 0.0)
            
            if not original_text:
                return ChatResponseFromSpeech(
                    success=False,
                    original_text="",
                    response="صدایی تشخیص داده نشد. لطفاً دوباره تلاش کنید.",
                    error="No speech detected"
                )
            
            logger.info(f"🎤 STT: '{original_text}' (confidence: {stt_confidence})")
            
            # ===== ۳. تشخیص Intent =====
            intent = await detect_intent_from_text(original_text)
            
            # ===== ۴. دریافت پاسخ از AI Assistant =====
            chat_service = ChatService()
            chat_result = await chat_service.process_message(
                message=original_text,
                user_id=user_id,
                language=language
            )
            
            response_text = chat_result.get("response", "متأسفانه پاسخی پیدا نشد.")
            source = chat_result.get("source", "database")
            confidence = chat_result.get("confidence", 0.0)
            suggestions = chat_result.get("suggestions", [])
            intent = chat_result.get("intent", intent)
            
            # ===== ۵. تبدیل پاسخ به گفتار =====
            audio_response = None
            if return_audio and response_text:
                voice_service = VoiceService()
                audio_response = voice_service.text_to_speech(
                    text=response_text,
                    language=language
                )
            
            # ===== ۶. پاسخ نهایی =====
            return ChatResponseFromSpeech(
                success=True,
                original_text=original_text,
                normalized_text=normalized_text,
                dialect=dialect,
                intent=intent,
                response=response_text,
                audio_response=audio_response,
                source=source,
                confidence=confidence,
                suggestions=suggestions,
                memory_usage=stt_result.get("memory_usage")
            )
            
        finally:
            try:
                os.unlink(audio_path)
            except:
                pass
            
    except Exception as e:
        logger.error(f"❌ Process error: {e}")
        return ChatResponseFromSpeech(
            success=False,
            original_text="",
            response=f"خطا: {str(e)}",
            error=str(e)
        )


@router.get(
    "/status",
    summary="وضعیت سرویس گفتار"
)
async def speech_status():
    """وضعیت سرویس تشخیص گفتار"""
    stt = get_speech_engine()
    return {
        "status": "active",
        "vosk": stt.health_check(),
        "bandari_engine": "http://127.0.0.1:5200",
        "pipeline": [
            "Vosk STT",
            "Bandari Engine",
            "Intent Detection",
            "RAG / Knowledge Graph",
            "AI Assistant"
        ]
    }


# ============================================================
# Helper Functions
# ============================================================

async def detect_intent_from_text(text: str) -> str:
    """تشخیص Intent از متن"""
    try:
        # ساده: از ChatService برای تشخیص استفاده کن
        chat_service = ChatService()
        result = await chat_service.process_message(
            message=text,
            user_id="intent_detector"
        )
        return result.get("intent", "general")
    except:
        return "general"
