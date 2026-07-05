"""Voice API Endpoints - Speech Recognition and Text-to-Speech"""

from fastapi import APIRouter, HTTPException, File, UploadFile, Query
from fastapi.responses import StreamingResponse
import io
from loguru import logger
from app.core.speech_interface import get_speech_interface
from app.services.chat_service import get_chat_service

router = APIRouter(prefix="/voice", tags=["voice"])

@router.post("/speech-to-text")
async def speech_to_text(file: UploadFile = File(...), language: str = Query("fa-IR")):
    """Convert speech to text from audio file"""
    logger.info(f"🎙️ Converting audio file to text (language: {language})")
    
    try:
        speech_interface = get_speech_interface()
        
        # Save uploaded file temporarily
        temp_file = f"/tmp/{file.filename}"
        with open(temp_file, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Convert to text
        text, confidence = speech_interface.speech_to_text(
            audio_file=temp_file,
            language=language
        )
        
        return {
            "status": "success",
            "text": text,
            "confidence": confidence,
            "file_name": file.filename
        }
    
    except Exception as e:
        logger.error(f"Speech-to-text error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/text-to-speech")
async def text_to_speech(text: str = Query(...), language: str = Query("fa")):
    """Convert text to speech"""
    logger.info(f"🔊 Converting text to speech: {text[:50]}...")
    
    try:
        speech_interface = get_speech_interface()
        
        # Get audio bytes
        audio_bytes = speech_interface.text_to_speech_bytes(text, language)
        
        if audio_bytes:
            return StreamingResponse(
                io.BytesIO(audio_bytes),
                media_type="audio/mpeg",
                headers={"Content-Disposition": "attachment; filename=audio.mp3"}
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to generate audio")
    
    except Exception as e:
        logger.error(f"Text-to-speech error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/voice-chat")
async def voice_chat(
    file: UploadFile = File(...),
    user_id: str = Query(...),
    language: str = Query("fa-IR")
):
    """End-to-end voice chat: speech-to-text -> chat -> text-to-speech"""
    logger.info(f"💬 Voice chat from user: {user_id}")
    
    try:
        speech_interface = get_speech_interface()
        chat_service = get_chat_service()
        
        # Step 1: Convert speech to text
        temp_file = f"/tmp/{file.filename}"
        with open(temp_file, "wb") as f:
            content = await file.read()
            f.write(content)
        
        user_message, stt_confidence = speech_interface.speech_to_text(
            audio_file=temp_file,
            language=language
        )
        
        if not user_message:
            raise HTTPException(status_code=400, detail="Could not understand audio")
        
        # Step 2: Process chat
        chat_result = chat_service.process_message(user_message, user_id)
        
        # Step 3: Convert response to speech
        response_text = chat_result["response"]
        response_audio = speech_interface.text_to_speech_bytes(
            response_text,
            language="fa"
        )
        
        return {
            "status": "success",
            "user_message": user_message,
            "stt_confidence": stt_confidence,
            "chat_response": response_text,
            "chat_intent": chat_result["intent"],
            "audio_url": "/api/v1/voice/text-to-speech?text=" + response_text.replace(" ", "%20")
        }
    
    except Exception as e:
        logger.error(f"Voice chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
