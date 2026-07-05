"""FastAPI Main Application Entry Point"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from app.api.v1 import routers
from app.core.logger import logger

# Load environment variables
load_dotenv()

# App Configuration
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
FASTAPI_ENV = os.getenv("FASTAPI_ENV", "development")
CORS_ORIGINS = os.getenv(
    "API_CORS_ORIGINS",
    "[\"http://localhost:3000\", \"http://localhost:8080\"]"
)

# Lifecycle Events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and Shutdown Events"""
    logger.info(f"🚀 Starting Hermezgan Intelligent API - {FASTAPI_ENV}")
    yield
    logger.info("🛑 Shutting down Hermezgan Intelligent API")

# Initialize FastAPI App
app = FastAPI(
    title="🌊 Hermezgan Intelligent - هرمزگان هوشمند",
    description="Knowledge Graph & AI System for Bandar Abbas",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=eval(CORS_ORIGINS),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health Check Endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "environment": FASTAPI_ENV,
            "debug": DEBUG
        }
    )

# Include V1 Routers
app.include_router(
    routers.router,
    prefix="/api/v1",
    tags=["v1"]
)

# Root Endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Hermezgan Intelligent API",
        "docs": "/api/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=DEBUG,
        log_level="info" if not DEBUG else "debug"
    )