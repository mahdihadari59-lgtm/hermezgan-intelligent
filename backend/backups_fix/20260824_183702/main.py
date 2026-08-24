# ============================================================
# Hermezgan Intelligent - FIXED main.py
# ============================================================
# FIXES:
# 1. Removed duplicate Copilot registration (3 times!)
# 2. Removed duplicate POI router
# 3. Added Weather Router
# 4. Added Routing/Navigation Router
# 5. Added Gemini AI Router
# 6. Added ElevenLabs TTS Router
# 7. Added lifespan for DB health check
# ============================================================

from fastapi import FastAPI, Depends, HTTPException, Query, Request
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

DB_PATH = os.getenv("DB_PATH", "./data/hormozgan_master_final.db")

# ============================================================
# Startup/Shutdown Events
# ============================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting Hermezgan Intelligent...")
    
    # Check database
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        table_count = cursor.fetchone()[0]
        logger.info(f"✅ Database: {table_count} tables")
        
        # Check critical tables
        for table in ["graph_entities", "graph_edges_rag", "pois", "tourism_poi"]:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                logger.info(f"   📊 {table}: {count} records")
            except:
                logger.warning(f"   ⚠️ {table}: missing/empty")
        conn.close()
    except Exception as e:
        logger.error(f"❌ DB Error: {e}")
    
    yield
    logger.info("🛑 Shutting down...")

# ============================================================
# FastAPI App
# ============================================================
app = FastAPI(
    title="هرمزگان هوشمند API",
    description="سیستم یکپارچه دانش‌گراف و هوش مصنوعی هرمزگان",
    version="2.0.0-fixed",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ============================================================
# CORS
# ============================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# V1 Routers (Unified - NO DUPLICATE!)
# ============================================================
# FIX: Only use routers.py, don't register pois directly!
try:
    from app.api.v1.routers import router as api_router
    app.include_router(api_router, prefix="/api/v1")
    logger.info("✅ V1 Routers registered (unified)")
except Exception as e:
    logger.error(f"❌ V1 Routers failed: {e}")

# ============================================================
# Chat & WebSocket
# ============================================================
try:
    from app.api.chat import router as chat_router
    app.include_router(chat_router, prefix="/api/v1", tags=["Chat"])
    logger.info("✅ Chat Router registered")
except Exception as e:
    logger.error(f"❌ Chat: {e}")

try:
    from app.api.ws import router as ws_router
    app.include_router(ws_router, prefix="/api/v1", tags=["WebSocket"])
    logger.info("✅ WebSocket Router registered")
except Exception as e:
    logger.error(f"❌ WebSocket: {e}")

# ============================================================
# Orchestrator (V3)
# ============================================================
try:
    from app.api.orchestrator import router as orchestrator_router
    app.include_router(
        orchestrator_router,
        prefix="/api/v1/orchestrator",
        tags=["Orchestrator"]
    )
    logger.info("✅ Orchestrator registered")
except Exception as e:
    logger.error(f"❌ Orchestrator: {e}")

# ============================================================
# Copilot (FIXED: Only ONCE!)
# ============================================================
try:
    from app.api.copilot import router as copilot_router
    app.include_router(
        copilot_router,
        prefix="/api/v1/copilot",
        tags=["Copilot"]
    )
    logger.info("✅ Copilot registered")
except Exception as e:
    logger.error(f"❌ Copilot: {e}")

# ============================================================
# NEW: Weather Router
# ============================================================
try:
    from app.api.v1.weather import router as weather_router
    app.include_router(
        weather_router,
        prefix="/api/v1/weather",
        tags=["Weather"]
    )
    logger.info("✅ Weather registered")
except Exception as e:
    logger.warning(f"⚠️ Weather not available: {e}")

# ============================================================
# NEW: Routing/Navigation Router
# ============================================================
try:
    from app.api.v1.routing import router as routing_router
    app.include_router(
        routing_router,
        prefix="/api/v1/routing",
        tags=["Routing"]
    )
    logger.info("✅ Routing registered")
except Exception as e:
    logger.warning(f"⚠️ Routing not available: {e}")

# ============================================================
# NEW: Gemini AI Router
# ============================================================
try:
    from app.api.v1.gemini import router as gemini_router
    app.include_router(
        gemini_router,
        prefix="/api/v1/ai",
        tags=["AI - Gemini"]
    )
    logger.info("✅ Gemini AI registered")
except Exception as e:
    logger.warning(f"⚠️ Gemini AI not available: {e}")

# ============================================================
# NEW: ElevenLabs TTS Router
# ============================================================
try:
    from app.api.v1.tts import router as tts_router
    app.include_router(
        tts_router,
        prefix="/api/v1/tts",
        tags=["TTS - ElevenLabs"]
    )
    logger.info("✅ ElevenLabs TTS registered")
except Exception as e:
    logger.warning(f"⚠️ ElevenLabs TTS not available: {e}")

# ============================================================
# Health Check (Enhanced)
# ============================================================
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
    except:
        services["database"] = "error"
    
    return {
        "status": "healthy",
        "version": "2.0.0-fixed",
        "services": services,
        "endpoints": {
            "docs": "/docs",
            "v1": "/api/v1",
            "chat": "/api/v1/chat",
            "orchestrator": "/api/v1/orchestrator/chat",
            "copilot": "/api/v1/copilot/message",
            "weather": "/api/v1/weather",
            "routing": "/api/v1/routing",
            "ai": "/api/v1/ai",
            "tts": "/api/v1/tts",
        }
    }

@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "خوش‌آمدید به هرمزگان هوشمند",
        "version": "2.0.0-fixed",
        "features": ["POI", "Chat", "Weather", "Routing", "Gemini AI", "ElevenLabs TTS"],
        "docs": "/docs"
    }

# ============================================================
# Exception Handler
# ============================================================
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "خطای داخلی سرور",
                "detail": str(exc) if os.getenv("DEBUG") == "true" else None
            }
        }
    )

# ============================================================
# Run
# ============================================================
if __name__ == "__main__":
    import uvicorn
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8001"))
    logger.info(f"🚀 Starting on {host}:{port}")
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
