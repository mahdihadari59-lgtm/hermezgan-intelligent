from app.api.v1.driver_assistant import router as driver_assistant_router
# ============================================================
# Hermezgan Intelligent - Safe Upgrade main.py
# ============================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import os
import logging
import sqlite3

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

DB_PATH = os.getenv("DB_PATH", "/data/data/com.termux/files/home/hormozgan_geo_project/hormozgan_data/hormozgan_master_final.db")


def _safe_include_router(app: FastAPI, router, prefix: str, **kwargs):
    """Register a router only if none of its endpoints already exist."""
    try:
        existing_paths = {route.path for route in app.routes}
        candidate_paths = [
            f"{prefix}{route.path}" if route.path.startswith("/") else f"{prefix}/{route.path}"
            for route in getattr(router, "routes", [])
        ]
        if any(candidate in existing_paths for candidate in candidate_paths):
            logger.info("Skipping already-registered router prefix=%s", prefix)
            return
        app.include_router(router, prefix=prefix, **kwargs)
    except Exception as exc:
        logger.warning("Router registration skipped for %s: %s", prefix, exc)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Hermezgan Intelligent...")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        logger.info(f"Database: {cursor.fetchone()[0]} tables")
        conn.close()
    except Exception as e:
        logger.error(f"DB Error: {e}")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="Hermezgan Intelligent API",
    description="Integrated Knowledge Graph and AI System for Hormozgan",
    version="2.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Safe compatibility registration strategy:
# - Keep legacy API v1 route set active.
# - Add new upgrade modules with unique prefixes.
# - Avoid duplicated route registrations.

try:
    from app.api.v1.routers import router as api_router
    _safe_include_router(app, api_router, prefix="/api/v1")
except Exception as e:
    logger.error(f"V1 Routers: {e}")

# New safe-upgrade modules with explicit unique prefixes.
try:
    from app.api.v1.system import router as system_router
    _safe_include_router(app, system_router, prefix="/api/v1/system")
    logger.info("System Router registered")
except Exception as e:
    logger.warning(f"System Router not available: {e}")

try:
    from app.api.v1.orchestrator import router as orchestrator_router
    _safe_include_router(app, orchestrator_router, prefix="/api/v1/orchestrator")
    logger.info("Orchestrator Router registered")
except Exception as e:
    logger.warning(f"Orchestrator Router not available: {e}")

# Chat & WebSocket
try:
    from app.api.chat import router as chat_router
    _safe_include_router(app, chat_router, prefix="/api/v1", tags=["Chat"])
    logger.info("Chat Router registered")
except Exception as e:
    logger.error(f"Chat: {e}")

try:
    from app.api.ws import router as ws_router
    _safe_include_router(app, ws_router, prefix="/api/v1", tags=["WebSocket"])
    logger.info("WebSocket Router registered")
except Exception as e:
    logger.error(f"WebSocket: {e}")

# Orchestrator (V3)
try:
    from app.api.orchestrator import router as orchestrator_v3_router
    _safe_include_router(app, orchestrator_v3_router, prefix="/api/v1/orchestrator", tags=["Orchestrator"])
    logger.info("V3 Orchestrator Router registered")
except Exception as e:
    logger.error(f"Orchestrator: {e}")

# Voice Router
try:
    from app.api.v1.voice import router as voice_router
    _safe_include_router(app, voice_router, prefix="/api/v1/voice", tags=["Voice"])
    logger.info("Voice Router registered")
except Exception as e:
    logger.warning(f"Voice not available: {e}")

# Copilot
try:
    from app.api.copilot import router as copilot_router
    _safe_include_router(app, copilot_router, prefix="/api/v1/copilot", tags=["Copilot"])
    logger.info("Copilot Router registered")
except Exception as e:
    logger.error(f"Copilot: {e}")

# Weather Router
try:
    from app.api.v1.weather import router as weather_router
    _safe_include_router(app, weather_router, prefix="/api/v1/weather", tags=["Weather"])
    logger.info("Weather Router registered")
except Exception as e:
    logger.warning(f"Weather not available: {e}")

# Routing/Navigation Router
try:
    from app.api.v1.routing import router as routing_router
    _safe_include_router(app, routing_router, prefix="/api/v1/routing", tags=["Routing"])
    logger.info("Routing Router registered")
except Exception as e:
    logger.warning(f"Routing not available: {e}")

# Driver Assistant Router
try:
    from app.api.v1.driver_assistant import router as driver_assistant_router
    _safe_include_router(app, driver_assistant_router, prefix="/api/v1/driver", tags=["Driver Assistant"])
    logger.info("Driver Assistant Router registered")
except Exception as e:
    logger.warning(f"Driver Assistant not available: {e}")

# Gemini AI Router
try:
    from app.api.v1.gemini import router as gemini_router
    _safe_include_router(app, gemini_router, prefix="/api/v1/ai", tags=["AI - Gemini"])
    logger.info("Gemini AI Router registered")
except Exception as e:
    logger.warning(f"Gemini AI not available: {e}")

# ElevenLabs TTS Router
try:
    from app.api.v1.tts import router as tts_router
    _safe_include_router(app, tts_router, prefix="/api/v1/tts", tags=["TTS - ElevenLabs"])
    logger.info("ElevenLabs TTS Router registered")
except Exception as e:
    logger.warning(f"ElevenLabs TTS not available: {e}")


@app.get("/health", tags=["Health"])
async def health_check():
    services = {
        "database": "unknown",
        "gemini": "configured" if os.getenv("GEMINI_API_KEY") else "missing",
        "elevenlabs": "configured" if os.getenv("ELEVENLABS_API_KEY") else "missing",
    }
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("SELECT 1")
        services["database"] = "connected"
        conn.close()
    except Exception:
        services["database"] = "error"

    return {
        "status": "healthy",
        "version": "2.1.0",
        "services": services,
        "endpoints": {
            "docs": "/docs",
            "v1": "/api/v1",
            "system": "/api/v1/system/status",
            "orchestrator": "/api/v1/orchestrator/health",
            "chat": "/api/v1/chat",
            "orchestrator_v3": "/api/v1/orchestrator/chat",
            "copilot": "/api/v1/copilot/message",
            "weather": "/api/v1/weather/current",
            "routing": "/api/v1/routing/directions",
            "ai": "/api/v1/ai/chat",
            "tts": "/api/v1/tts/speak",
        }
    }


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to Hermezgan Intelligent",
        "version": "2.1.0",
        "upgrade_mode": "safe_incremental",
        "features": ["POI", "Chat", "Weather", "Routing", "Gemini AI", "ElevenLabs TTS", "System", "Orchestrator"],
        "docs": "/docs"
    }


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "Internal server error",
                "detail": str(exc) if os.getenv("DEBUG") == "true" else None
            }
        }
    )


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8001"))
    logger.info(f"Starting on {host}:{port}")
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
