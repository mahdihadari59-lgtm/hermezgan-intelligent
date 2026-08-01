from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatMessage(BaseModel):
    message: str
    user_id: str = "anonymous"
    language: str = "fa"

@router.post("/send")
async def send_message(msg: ChatMessage):
    try:
        chat = ChatService()
        return await chat.process_message(msg.message, msg.user_id, language=msg.language)
    except Exception as e:
        raise HTTPException(500, str(e))
