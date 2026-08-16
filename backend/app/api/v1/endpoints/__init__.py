# app/api/v1/endpoints/__init__.py
from .chat import router as chat_router
from .locations import router as locations_router
from .analytics import router as analytics_router
from .cameras import router as cameras_router
from .hotspots import router as hotspots_router
from .traffic import router as traffic_router

# تابع health برای main.py
async def health():
    return {"status": "ok"}

__all__ = [
    "chat_router",
    "locations_router",
    "analytics_router",
    "cameras_router",
    "hotspots_router",
    "traffic_router",
    "health",
]
