"""API V1 Router Configuration"""

from fastapi import APIRouter
from app.api.v1.endpoints import chat, locations

router = APIRouter()

# Include endpoint routers
router.include_router(chat.router)
router.include_router(locations.router)

# Chat Endpoints
@router.post("/chat/message")
async def send_message(message: str):
    """Send a message to the chat bot"""
    return {"response": "Chat endpoint - use POST /api/v1/chat/message with ChatMessage schema"}

# Knowledge Graph Endpoints
@router.get("/graph/entities")
async def get_entities():
    """Get all entities from knowledge graph"""
    return {"entities": []}

@router.get("/graph/relations")
async def get_relations():
    """Get all relations from knowledge graph"""
    return {"relations": []}

# Analytics Endpoints
@router.get("/analytics/stats")
async def get_statistics():
    """Get system statistics"""
    return {"stats": {}}
