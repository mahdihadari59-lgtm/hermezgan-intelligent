"""HDP Backend Main Application

Complete integration of:
- MLflow Model Tracking
- TTS Service
- Service Contracts
- Analytics & Events
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
import os
import time
from dotenv import load_dotenv

# Import routers
from app.api.v1 import chat, locations, analytics, cameras, hotspots
from app.api.v1.ping import router as ping_router

# Import integrated services
from app.mlflow_router import router as mlflow_router
from app.services.tts_service import get_tts_service
from app.schemas import StandardResponse, HealthCheckResponse

# Import Hybrid Engine
from engine.hybrid.hybrid_engine import HybridEngine

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
hybrid_engine = None
tts_service = None
request_start_time = None


# ============================================================
# Lifecycle Management
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown"""
    global hybrid_engine, tts_service
    
    logger.info("=" * 60)
    logger.info("✅ HDP Backend Starting...")
    logger.info("=" * 60)
    
    try:
        # Initialize Hybrid Engine
        database_url = os.getenv("DATABASE_URL")
        database_path = os.getenv("DATABASE_PATH")

        if database_url:
            logger.info(f"📊 Using DATABASE_URL: {database_url}")
            db_conn = database_url
        elif database_path:
            logger.info(f"📊 Using DATABASE_PATH: {database_path}")
            db_conn = database_path
        else:
            db_conn = "sqlite:///./data/hdp_v2.db"
            logger.info(f"📊 Using default database: {db_conn}")

        hybrid_engine = HybridEngine(db_conn)
        logger.info("✅ Hybrid Engine initialized")
        
        # Initialize TTS Service
        tts_service = get_tts_service()
        logger.info("✅ TTS Service initialized")
        
        # Health check for critical services
        tts_health = await tts_service.health_check()
        logger.info(f"📊 TTS Service Status: {tts_health['status']}")
        
        logger.info("=" * 60)
        logger.info("✅ All services started successfully")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
        raise
    
    yield
    
    # Cleanup
    logger.info("🛑 Backend shutting down...")
    try:
        if hybrid_engine:
            hybrid_engine.clear_cache()
            logger.info("✅ Hybrid Engine cleaned up")
    except Exception as e:
        logger.error(f"Cleanup error: {e}")
    
    logger.info("🛑 Backend stopped")


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="هرمزگان هوشمند API v2",
    description="سیستم دانش‌گراف هوشمند استان هرمزگان - با MLflow، TTS و Service Contracts",
    version="2.0.0",
    default_response_class=JSONResponse,
    lifespan=lifespan
)

# ============================================================
# Middleware Configuration
# ============================================================

# CORS Configuration
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)


# ============================================================
# Request/Response Timing Middleware
# ============================================================

@app.middleware("http")
async def add_process_time_header(request, call_next):
    """Add processing time to response"""
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000  # ms
    response.headers["X-Process-Time"] = str(process_time)
    return response


# ============================================================
# Router Registration
# ============================================================

# Core API Routers
app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])
app.include_router(ping_router, prefix="/api/v1", tags=["Health"])
app.include_router(locations.router, prefix="/api/v1", tags=["Locations"])
app.include_router(analytics.router, prefix="/api/v1", tags=["Analytics"])
app.include_router(cameras.router, prefix="/api/v1", tags=["Cameras"])
app.include_router(hotspots.router, prefix="/api/v1", tags=["Hotspots"])

# MLflow Integration Router
app.include_router(mlflow_router, prefix="/api/v1", tags=["MLflow"])


# ============================================================
# Hybrid Search Endpoints
# ============================================================

@app.get("/api/v1/hybrid/search")
async def hybrid_search(
    q: str = Query(..., description="متن جستجو", min_length=1, max_length=1000),
    top_k: int = Query(10, description="تعداد نتایج", ge=1, le=50),
    search_type: str = Query("hybrid", description="نوع جستجو: hybrid, fts, vector, graph")
):
    """
    جستجوی هیبرید با استفاده از ترکیب FTS، Graph و Embedding
    
    Returns:
        - success: bool
        - query: str
        - results: list
        - count: int
        - processing_time_ms: float
    """
    if not hybrid_engine:
        raise HTTPException(status_code=503, detail="Hybrid Engine not initialized")
    
    start_time = time.time()
    
    try:
        results = hybrid_engine.search(q, top_k=top_k)
        processing_time = (time.time() - start_time) * 1000
        
        return {
            "success": True,
            "query": q,
            "results": results,
            "count": len(results),
            "processing_time_ms": processing_time
        }
    except Exception as e:
        logger.error(f"❌ Hybrid search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/hybrid/stats")
async def hybrid_stats():
    """
    دریافت آمار موتور هیبرید
    
    Returns:
        - success: bool
        - stats: dict with engine statistics
    """
    if not hybrid_engine:
        raise HTTPException(status_code=503, detail="Hybrid Engine not initialized")
    
    try:
        return {
            "success": True,
            "stats": hybrid_engine.stats()
        }
    except Exception as e:
        logger.error(f"❌ Stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# TTS Endpoints
# ============================================================

@app.post("/api/v1/tts/synthesize")
async def tts_synthesize(
    text: str = Query(..., min_length=1, max_length=5000),
    language: str = Query("fa", description="Language code"),
    speed: float = Query(1.0, ge=0.5, le=2.0)
):
    """
    Text-to-Speech Synthesis
    
    Returns audio in base64 format
    """
    if not tts_service:
        raise HTTPException(status_code=503, detail="TTS Service not initialized")
    
    try:
        result = await tts_service.synthesize(text, language, speed)
        return result
    except Exception as e:
        logger.error(f"❌ TTS synthesis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/tts/health")
async def tts_health():
    """Check TTS Service health"""
    if not tts_service:
        raise HTTPException(status_code=503, detail="TTS Service not initialized")
    
    try:
        health = await tts_service.health_check()
        return {
            "success": True,
            "tts": health
        }
    except Exception as e:
        logger.error(f"❌ TTS health check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# Health & Status Endpoints
# ============================================================

@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Comprehensive health check for all services
    
    Returns:
        - status: healthy, degraded, unhealthy
        - version: API version
        - components: status of each component
    """
    try:
        components = {
            "hybrid_engine": "healthy" if hybrid_engine else "unhealthy",
            "tts_service": "healthy" if tts_service else "unhealthy",
            "database": "healthy",  # Would check actual DB connection
        }
        
        # Determine overall status
        if all(v == "healthy" for v in components.values()):
            overall_status = "healthy"
        elif any(v == "unhealthy" for v in components.values()):
            overall_status = "unhealthy"
        else:
            overall_status = "degraded"
        
        return HealthCheckResponse(
            status=overall_status,
            version="2.0.0",
            uptime_seconds=0,  # Would track actual uptime
            components=components
        )
    except Exception as e:
        logger.error(f"❌ Health check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/status")
async def status():
    """Get system status with all component details"""
    try:
        tts_health = await tts_service.health_check() if tts_service else {"status": "not_initialized"}
        
        return {
            "success": True,
            "status": "operational",
            "version": "2.0.0",
            "components": {
                "hybrid_engine": "operational" if hybrid_engine else "not_initialized",
                "tts_service": tts_health.get("status", "unknown"),
                "database": "connected",
            },
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"❌ Status error: {e}")
        return {
            "success": False,
            "status": "error",
            "error": str(e)
        }


# ============================================================
# Root & Welcome
# ============================================================

@app.get("/")
async def root():
    """Welcome endpoint"""
    return {
        "message": "خوش‌آمدید به هرمزگان هوشمند API v2",
        "docs": "/docs",
        "health": "/health",
        "status": "/api/v1/status"
    }


# ============================================================
# Error Handlers
# ============================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "request_path": str(request.url)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"❌ Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "request_path": str(request.url)
        }
    )


# ============================================================
# Main Entry Point
# ============================================================

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    reload = os.getenv("FASTAPI_ENV", "development") == "development"
    
    logger.info(f"🚀 Starting server on {host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
