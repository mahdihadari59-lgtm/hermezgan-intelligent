# ============================================================
# system.py - وضعیت و نمای کلی ساختار جدید پروژه
# ============================================================
from fastapi import APIRouter
from datetime import datetime
import os

router = APIRouter(prefix="/system", tags=["System"])


@router.get("/status")
async def system_status():
    return {
        "status": "ok",
        "version": "2.1.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "services": {
            "database": "configured" if os.getenv("DB_PATH") else "default",
            "gemini": "configured" if os.getenv("GEMINI_API_KEY") else "not_configured",
            "elevenlabs": "configured" if os.getenv("ELEVENLABS_API_KEY") else "not_configured",
        },
    }


@router.get("/overview")
async def system_overview():
    return {
        "project": "Hermezgan Intelligent",
        "version": "2.1.0",
        "structure": {
            "core": [
                "api",
                "services",
                "database",
                "knowledge",
                "routing",
                "orientation",
                "external_providers",
            ],
            "modules": [
                "chat",
                "copilot",
                "weather",
                "routing",
                "driver_assistant",
                "gemini_ai",
                "tts",
                "analytics",
                "health",
                "pois",
            ],
        },
        "upgrade": {
            "approach": "safe_and_incremental",
            "goal": "add new unified architecture without breaking existing systems",
            "compatibility": "legacy routers remain available while new endpoints are introduced",
        },
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
