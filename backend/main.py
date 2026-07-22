from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZIPMiddleware
from fastapi.responses import ORJSONResponse
from contextlib import asynccontextmanager
import logging
import os
from dotenv import load_dotenv

load_dotenv()

from app.api.v1 import chat, locations, analytics, cameras, hotspots

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("✅ Backend started")
    yield
    logger.info("🛑 Backend shutting down")

app = FastAPI(
    title="هرمزگان هوشمند API",
    description="سیستم دانش‌گراف هوشمند استان هرمزگان",
    version="1.0.0",
    default_response_class=ORJSONResponse,
    lifespan=lifespan
)

app.add_middleware(GZIPMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])
app.include_router(locations.router, prefix="/api/v1", tags=["Locations"])
app.include_router(analytics.router, prefix="/api/v1", tags=["Analytics"])
app.include_router(cameras.router, prefix="/api/v1", tags=["Cameras"])
app.include_router(hotspots.router, prefix="/api/v1", tags=["Hotspots"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

@app.get("/")
async def root():
    return {"message": "خوش‌آمدید به هرمزگان هوشمند"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
