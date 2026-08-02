from fastapi import APIRouter

from .health import router as health_router
from .ping import router as ping_router
from .auth import router as auth_router
from .endpoints.chat import router as chat_router
from .analytics import router as analytics_router
from .traffic import router as traffic_router
from .tourism import router as tourism_router
from .hospitals import router as hospitals_router
from .fuel import router as fuel_router
from .weather import router as weather_router
from .emergency import router as emergency_router
from .municipality import router as municipality_router
from .ai import router as ai_router
from .bandari import router as bandari_router
from .search import router as search_router

api_router = APIRouter()

for router in (
    health_router,
    ping_router,
    auth_router,
    chat_router,
    analytics_router,
    traffic_router,
    tourism_router,
    hospitals_router,
    fuel_router,
    weather_router,
    emergency_router,
    municipality_router,
    ai_router,
    bandari_router,
    search_router,
):
    api_router.include_router(router)
