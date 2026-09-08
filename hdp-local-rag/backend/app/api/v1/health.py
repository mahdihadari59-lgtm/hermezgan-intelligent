# ============================================================
# health.py - API بررسی سلامت
# ============================================================
from fastapi import APIRouter
from datetime import datetime
import os

router = APIRouter()


@router.get("/")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "timestamp": datetime.now().isoformat()
    }


@router.get("/ping")
async def ping():
    return {"status": "pong", "timestamp": datetime.now().isoformat()}
