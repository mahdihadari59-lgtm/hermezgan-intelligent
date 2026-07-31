from fastapi import APIRouter

from .ping import router as ping_router
from .endpoints.chat import router as chat_router
from .endpoints.voice import router as voice_router
from .endpoints.locations import router as locations_router

router = APIRouter()

# Health Check
router.include_router(ping_router)

# Chat API
router.include_router(chat_router)

# Voice API
router.include_router(voice_router)

# Location API
router.include_router(locations_router)
