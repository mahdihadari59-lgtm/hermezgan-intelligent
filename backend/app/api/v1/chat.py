from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter(prefix="/chat", tags=["Chat"])

class ChatMessage(BaseModel):
    message: str
    user_id: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class ChatResponse(BaseModel):
    response: str
    intent: str
    confidence: float
    suggestions: List[str] = []

@router.post("/message", response_model=ChatResponse)
async def send_message(data: ChatMessage):
    return ChatResponse(
        response=f"دریافت شد: {data.message}",
        intent="general",
        confidence=0.95,
        suggestions=["🏥 بیمارستان", "🍽️ رستوران", "🚗 تاکسی"]
    )
