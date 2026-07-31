"""Chat API Endpoints"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, Dict, List
from loguru import logger

from app.services.chat_service import ChatService
from app.dependencies.services import get_chat_service

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
    suggestions: List[str] = []
    retrieved_documents: list


@router.post("/message", response_model=ChatResponse)
async def send_message(
    chat_msg: ChatMessage,
    chat_service: ChatService = Depends(get_chat_service),
) -> Dict:
    """Send a message to chat bot"""
    logger.info(f"📨 Received chat message from {chat_msg.user_id}")

    try:
        # BUG FIX (original code): `chat_service = get_chat_service()` was
        # called as a bare function inside the route body, so FastAPI never
        # actually resolved the `Depends(get_db)` / `Depends(get_copilot_gateway)`
        # defaults on get_chat_service — `db` ended up being the literal
        # `Depends(...)` marker object, not a real Session. Using it as a
        # route parameter (`= Depends(get_chat_service)`) makes FastAPI
        # resolve the whole dependency chain (db -> gateway -> hotspot/camera/
        # analytics services) properly before the handler runs.

        # BUG FIX (original code): a `user_location` dict was built and
        # passed as the positional `latitude` argument, silently breaking
        # every location-aware branch. Pass lat/lon directly instead.
        result = await chat_service.process_message(
            chat_msg.message,
            chat_msg.user_id,
            latitude=chat_msg.latitude,
            longitude=chat_msg.longitude,
        )

        return ChatResponse(
            response=result["response"],
            intent=result["intent"],
            confidence=result["confidence"],
            suggestions=result.get("suggestions", []),
            retrieved_documents=result["retrieved_documents"],
        )

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_chat_history(
    user_id: str = Query(...),
    limit: int = Query(50, le=200),
    chat_service: ChatService = Depends(get_chat_service),
):
    """Get chat history for a user"""
    logger.info(f"📖 Fetching chat history for {user_id}")

    try:
        history = chat_service.get_chat_history(user_id, limit)
        return {"user_id": user_id, "messages": history}
    except Exception as e:
        logger.error(f"History fetch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
