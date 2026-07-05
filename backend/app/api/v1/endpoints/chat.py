"""Chat API Endpoints"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, Dict
from loguru import logger
from app.services.chat_service import get_chat_service

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatMessage(BaseModel):
    """Chat Message Request"""
    message: str
    user_id: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class ChatResponse(BaseModel):
    """Chat Response"""
    response: str
    intent: str
    confidence: float
    retrieved_documents: list

@router.post("/message", response_model=ChatResponse)
async def send_message(chat_msg: ChatMessage) -> Dict:
    """Send a message to chat bot"""
    logger.info(f"📨 Received chat message from {chat_msg.user_id}")
    
    try:
        chat_service = get_chat_service()
        
        # Prepare user location if provided
        user_location = None
        if chat_msg.latitude and chat_msg.longitude:
            user_location = {
                "latitude": chat_msg.latitude,
                "longitude": chat_msg.longitude,
            }
        
        # Process message
        result = chat_service.process_message(
            chat_msg.message,
            chat_msg.user_id,
            user_location
        )
        
        return ChatResponse(
            response=result["response"],
            intent=result["intent"],
            confidence=result["confidence"],
            retrieved_documents=result["retrieved_documents"]
        )
    
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_chat_history(user_id: str = Query(...), limit: int = Query(50, le=200)):
    """Get chat history for a user"""
    logger.info(f"📖 Fetching chat history for {user_id}")
    
    try:
        chat_service = get_chat_service()
        history = chat_service.get_chat_history(user_id, limit)
        return {"user_id": user_id, "messages": history}
    
    except Exception as e:
        logger.error(f"History fetch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
