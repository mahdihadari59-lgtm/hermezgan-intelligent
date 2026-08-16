# ============================================================
# main.py - فایل اصلی FastAPI
# ============================================================
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
import logging

# بارگذاری متغیرهای محیطی
load_dotenv()

# تنظیم لاگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ایجاد برنامه FastAPI
app = FastAPI(
    title="هرمزگان هوشمند API",
    description="سیستم دانش‌گراف هوشمند استان هرمزگان",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ============================================================
# تنظیمات CORS
# ============================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5000",
        "https://hermezgan.ir",
        "https://www.hermezgan.ir"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# ثبت Routerها
# ============================================================

# ثبت Router POI
try:
    from app.api.v1.pois import router as pois_router
    app.include_router(pois_router, prefix="/api/v1/pois", tags=["POI"])
    logger.info("✅ Router POI ثبت شد")
except Exception as e:
    logger.error(f"❌ خطا در ثبت Router POI: {e}")

# ثبت سایر Routerها
try:
    from app.api.v1.routers import router as api_router
    app.include_router(api_router, prefix="/api/v1")
    logger.info("✅ Routerهای دیگر ثبت شدند")
except Exception as e:
    logger.error(f"❌ خطا در ثبت Routerهای دیگر: {e}")

# ============================================================
# Health Check
# ============================================================
@app.get("/health", tags=["Health"])
async def health_check():
    """بررسی سلامت سرویس"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@app.get("/", tags=["Root"])
async def root():
    """صفحه اصلی API"""
    return {
        "message": "خوش‌آمدید به هرمزگان هوشمند",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# ============================================================
# Exception Handlers
# ============================================================
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """مدیریت خطاهای عمومی"""
    logger.error(f"خطای غیرمنتظره: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "خطای داخلی سرور رخ داده است",
                "detail": str(exc) if os.getenv("DEBUG", "False").lower() == "true" else None
            }
        }
    )

# ============================================================
# اجرا
# ============================================================
if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    reload = os.getenv("ENVIRONMENT", "development") == "development"
    
    logger.info(f"🚀 راه‌اندازی سرور در {host}:{port}")
    logger.info(f"📚 مستندات: http://localhost:{port}/docs")
    logger.info(f"🔍 سلامت: http://localhost:{port}/health")
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        workers=1 if reload else 4
    )
