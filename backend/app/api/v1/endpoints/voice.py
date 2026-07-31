"""Voice API Endpoints - Speech Recognition and Text-to-Speech"""

import io
import os
import shutil
import tempfile

from fastapi import APIRouter, HTTPException, File, UploadFile, Query
from fastapi.responses import StreamingResponse
from loguru import logger

from app.core.speech_interface import get_speech_interface
from app.dependencies.services import get_chat_service

router = APIRouter(prefix="/voice", tags=["voice"])


@router.post("/speech-to-text")
async def speech_to_text(
    file: UploadFile = File(...),
    language: str = Query("fa-IR"),
):
    """Convert speech to text from audio file."""

    temp_file = None

    try:
        speech_interface = get_speech_interface()

        suffix = os.path.splitext(file.filename or "")[1] or ".wav"

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            temp_file = tmp.name
            shutil.copyfileobj(file.file, tmp)

        text, confidence = speech_interface.speech_to_text(
            audio_file=temp_file,
            language=language,
        )

        return {
            "status": "success",
            "text": text,
            "confidence": confidence,
            "file_name": file.filename,
        }

    except Exception as e:
        logger.exception("Speech-to-text failed")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if temp_file and os.path.exists(temp_file):
            try:
                os.unlink(temp_file)
            except Exception:
                pass


@router.post("/text-to-speech")
async def text_to_speech(
    text: str = Query(...),
    language: str = Query("fa"),
):
    """Convert text to speech."""

    try:
        speech_interface = get_speech_interface()

        audio_bytes = speech_interface.text_to_speech_bytes(
            text=text,
            language=language,
        )

        if not audio_bytes:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate speech",
            )

        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=speech.mp3"
            },
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.exception("Text-to-speech failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/voice-chat")
async def voice_chat(
    file: UploadFile = File(...),
    user_id: str = Query(...),
    language: str = Query("fa-IR"),
):
    """Speech → Chat → Speech."""

    temp_file = None

    try:
        speech_interface = get_speech_interface()
        chat_service = get_chat_service()

        suffix = os.path.splitext(file.filename or "")[1] or ".wav"

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            temp_file = tmp.name
            shutil.copyfileobj(file.file, tmp)

        user_message, confidence = speech_interface.speech_to_text(
            audio_file=temp_file,
            language=language,
        )

        if not user_message:
            raise HTTPException(
                status_code=400,
                detail="Could not recognize speech",
            )

        chat_result = chat_service.process_message(
            user_message,
            user_id,
        )

        response_text = chat_result["response"]

        return {
            "status": "success",
            "user_message": user_message,
            "stt_confidence": confidence,
            "chat_response": response_text,
            "chat_intent": chat_result.get("intent"),
            "audio_url": (
                "/api/v1/voice/text-to-speech?text="
                + response_text.replace(" ", "%20")
            ),
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.exception("Voice chat failed")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if temp_file and os.path.exists(temp_file):
            try:
                os.unlink(temp_file)
            except Exception:
                pass
