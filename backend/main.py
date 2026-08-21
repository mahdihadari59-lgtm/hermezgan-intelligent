# backend/app/main.py
import os
import time
import logging
from contextlib import asynccontextmanager
from logging.handlers import RotatingFileHandler
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# بارگذاری محیط
load_dotenv()

# ==================== تنظیمات ====================
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8001))
DATABASE_PATH = os.getenv("DATABASE_PATH", "./hormozgan_data/hormozgan_geodata.db")

# ==================== لاگینگ ====================
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

logger = logging.getLogger("hermezgan")
logger.setLevel(logging.INFO)

if not logger.handlers:
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)

    # File handler (rotating)
    file_handler = RotatingFileHandler(
        f"{log_dir}/hermezgan.log",
        maxBytes=10_000_000,
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_format = logging.Formatter(
        '{"time":"%(asctime)s","name":"%(name)s","level":"%(levelname)s","message":"%(message)s"}',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

# ==================== روترها ====================
from app.api.v1.endpoints import (
    chat_router,
    locations_router,
    analytics_router,
    cameras_router,
    hotspots_router,
    traffic_router,
)

# ==================== Lifespan ====================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """مدیریت چرخه حیات برنامه"""
    logger.info(f"🚀 راه‌اندازی هرمزگان هوشمند v{APP_VERSION}")

    # اتصال به دیتابیس
    app.state.start_time = time.time()
    app.state.db_connected = False

    try:
        import sqlite3
        
        # بررسی وجود فایل دیتابیس
        if not os.path.exists(DATABASE_PATH):
            raise FileNotFoundError(f"فایل دیتابیس یافت نشد: {DATABASE_PATH}")
        
        # تست اتصال
        conn = sqlite3.connect(DATABASE_PATH)
        conn.execute("SELECT 1")
        conn.close()
        
        app.state.db_connected = True
        logger.info(f"✅ دیتابیس متصل شد: {DATABASE_PATH}")
        
    except FileNotFoundError as e:
        logger.error(f"❌ {e}")
        app.state.db_connected = False
    except Exception as e:
        logger.error(f"❌ خطا در اتصال دیتابیس: {e}")
        app.state.db_connected = False

    yield

    logger.info("🛑 خاموش‌سازی هرمزگان هوشمند")

# ==================== اپلیکیشن ====================
app = FastAPI(
    title="هرمزگان هوشمند API",
    description="سیستم دانش‌گراف هوشمند استان هرمزگان",
    version=APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs" if DEBUG else None,
    redoc_url="/redoc" if DEBUG else None,
)

# ==================== میان‌افزارها ====================
# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZIP فشرده‌سازی
app.add_middleware(GZipMiddleware, minimum_size=1000)

# ==================== هندلر خطاها ====================
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """هندلر سراسری خطاها"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": str(exc) if DEBUG else "خطای داخلی سرور"
        }
    )

# ==================== روترها ====================
app.include_router(chat_router, prefix="/api/v1")
app.include_router(locations_router, prefix="/api/v1")
app.include_router(analytics_router, prefix="/api/v1")
app.include_router(cameras_router, prefix="/api/v1")
app.include_router(hotspots_router, prefix="/api/v1")
app.include_router(traffic_router, prefix="/api/v1")

# ==================== Endpoints عمومی ====================
@app.get("/")
async def root():
    """صفحه اصلی"""
    return {
        "name": "هرمزگان هوشمند",
        "version": APP_VERSION,
        "status": "online",
        "docs": "/docs" if DEBUG else None,
        "debug": DEBUG
    }

@app.get("/health")
async def health_check():
    """بررسی سلامت سیستم"""
    status = {
        "status": "healthy",
        "version": APP_VERSION,
        "uptime": round(time.time() - app.state.start_time, 1),
        "database": "connected" if app.state.db_connected else "disconnected",
        "debug": DEBUG
    }
    
    # اگر دیتابیس متصل نیست، وضعیت را تغییر دهید
    if not app.state.db_connected:
        status["status"] = "degraded"
        status["message"] = "Database connection failed"
    
    return status

# ==================== اجرا ====================
if __name__ == "__main__":
    import uvicorn
    
    # تنظیمات اجرا
    workers = int(os.getenv("WORKERS", 1))
    reload = DEBUG
    
    # در حالت DEBUG، workers را 1 قرار دهید
    if DEBUG:
        workers = 1
    
    logger.info(f"🚀 اجرا روی {API_HOST}:{API_PORT}")
    logger.info(f"📡 DEBUG: {DEBUG}, Workers: {workers}")
    
    uvicorn.run(
        "app.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=reload,
        workers=workers,
        log_level="info" if DEBUG else "warning",
    )
