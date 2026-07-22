from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
import uuid

from app.database.session import get_db
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["Chat"])

class ChatMessageRequest(BaseModel):
    message: str
    user_id: str = "anonymous"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    session_id: Optional[str] = None

class ChatMessageResponse(BaseModel):
    response: str
    intent: str
    confidence: float
    suggestions: List[str] = []
    processing_time: float
    from_cache: bool = False
    message_id: Optional[int] = None
    session_id: Optional[str] = None

class ConversationResponse(BaseModel):
    session_id: str
    messages: List[dict]
    total: int

class RatingRequest(BaseModel):
    message_id: int
    helpful: bool

@router.post("/message", response_model=ChatMessageResponse)
async def send_message(
    data: ChatMessageRequest,
    db: Session = Depends(get_db)
):
    try:
        chat_service = ChatService(db)
        session_id = data.session_id or str(uuid.uuid4())
        
        response = await chat_service.process_message(
            user_id=data.user_id,
            message=data.message,
            latitude=data.latitude,
            longitude=data.longitude,
            session_id=session_id
        )
        
        response['session_id'] = session_id
        return ChatMessageResponse(**response)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطا در پردازش پیام: {str(e)}")

@router.get("/history/{session_id}", response_model=ConversationResponse)
async def get_conversation_history(
    session_id: str,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    try:
        chat_service = ChatService(db)
        messages = chat_service.get_conversation_history(session_id, limit)
        
        return ConversationResponse(
            session_id=session_id,
            messages=messages,
            total=len(messages)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطا در دریافت تاریخچه: {str(e)}")

@router.post("/rate")
async def rate_response(
    data: RatingRequest,
    db: Session = Depends(get_db)
):
    try:
        chat_service = ChatService(db)
        success = chat_service.rate_response(data.message_id, data.helpful)
        
        if not success:
            raise HTTPException(status_code=404, detail="پیام یافت نشد")
        
        return {"status": "rated", "message_id": data.message_id, "helpful": data.helpful}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطا در ارزیابی: {str(e)}")

@router.get("/stats")
async def get_chat_stats(db: Session = Depends(get_db)):
    from app.models.chat import ChatMessage, ChatConversation
    
    total_messages = db.query(ChatMessage).count()
    total_conversations = db.query(ChatConversation).count()
    
    avg_processing_time = db.query(
        func.avg(ChatMessage.processing_time)
    ).scalar()
    
    intents = db.query(
        ChatMessage.intent,
        func.count(ChatMessage.id).label('count')
    ).group_by(ChatMessage.intent).all()
    
    return {
        "total_messages": total_messages,
        "total_conversations": total_conversations,
        "avg_processing_time": round(avg_processing_time or 0, 3),
        "intents": [{"intent": i[0], "count": i[1]} for i in intents]
    }
