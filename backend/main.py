from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import os
from dotenv import load_dotenv

from app.api.v1 import chat, locations, analytics, cameras, hotspots
from app.api.v1.ping import router as ping_router

# Import Hybrid Engine
from engine.hybrid.hybrid_engine import HybridEngine

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instance
hybrid_engine = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global hybrid_engine
    logger.info("✅ Backend started")
    
    # Initialize Hybrid Engine
    db_path = os.getenv("DATABASE_PATH", "data/hdp_v2.db")
    hybrid_engine = HybridEngine(db_path)
    logger.info(f"✅ Hybrid Engine initialized with db: {db_path}")
    
    yield
    
    # Cleanup
    if hybrid_engine:
        hybrid_engine.clear_cache()
        logger.info("✅ Hybrid Engine cleaned up")
    logger.info("🛑 Backend shutting down")

app = FastAPI(
    title="هرمزگان هوشمند API",
    description="سیستم دانش‌گراف هوشمند استان هرمزگان",
    version="1.0.0",
    default_response_class=JSONResponse,
    lifespan=lifespan
)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])
app.include_router(ping_router, prefix="/api/v1", tags=["Ping"])
app.include_router(locations.router, prefix="/api/v1", tags=["Locations"])
app.include_router(ping_router, prefix="/api/v1", tags=["Ping"])
app.include_router(analytics.router, prefix="/api/v1", tags=["Analytics"])
app.include_router(ping_router, prefix="/api/v1", tags=["Ping"])
app.include_router(cameras.router, prefix="/api/v1", tags=["Cameras"])
app.include_router(ping_router, prefix="/api/v1", tags=["Ping"])
app.include_router(hotspots.router, prefix="/api/v1", tags=["Hotspots"])
app.include_router(ping_router, prefix="/api/v1", tags=["Ping"])

# ============================================================
# Hybrid Search Endpoint
# ============================================================
@app.get("/api/v1/hybrid/search")
async def hybrid_search(
    q: str = Query(..., description="متن جستجو"),
    top_k: int = Query(10, description="تعداد نتایج", ge=1, le=50)
):
    """
    جستجوی هیبرید با استفاده از ترکیب FTS، Graph و Embedding
    """
    if not hybrid_engine:
        raise HTTPException(status_code=503, detail="Hybrid Engine not initialized")
    
    try:
        results = hybrid_engine.search(q, top_k=top_k)
        return {
            "success": True,
            "query": q,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"Hybrid search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/hybrid/stats")
async def hybrid_stats():
    """
    دریافت آمار موتور هیبرید
    """
    if not hybrid_engine:
        raise HTTPException(status_code=503, detail="Hybrid Engine not initialized")
    
    return {
        "success": True,
        "stats": hybrid_engine.stats()
    }

# ============================================================
# Health & Root
# ============================================================
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0", "hybrid_engine": hybrid_engine is not None}

@app.get("/")
async def root():
    return {"message": "خوش‌آمدید به هرمزگان هوشمند"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
