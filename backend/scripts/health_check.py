#!/usr/bin/env python
"""
اسکریپت بررسی سلامت سیستم
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
from app.core.config import settings
from app.core.database import get_db_session
from app.core.engine.redis_engine import get_redis_engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_database():
    try:
        db = get_db_session()
        db.execute("SELECT 1")
        db.close()
        return {"status": "healthy", "message": "دیتابیس در دسترس است"}
    except Exception as e:
        return {"status": "unhealthy", "message": str(e)}


def check_redis():
    try:
        redis = get_redis_engine()
        if redis.is_connected:
            return {"status": "healthy", "message": "Redis در دسترس است"}
        return {"status": "unhealthy", "message": "Redis در دسترس نیست"}
    except Exception as e:
        return {"status": "unhealthy", "message": str(e)}


def check_api():
    try:
        url = f"http://{settings.API_HOST}:{settings.API_PORT}/health"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return {"status": "healthy", "message": "API در دسترس است"}
        return {"status": "unhealthy", "message": f"API خطا: {response.status_code}"}
    except Exception as e:
        return {"status": "unhealthy", "message": str(e)}


def check_disk_space():
    try:
        import shutil
        total, used, free = shutil.disk_usage("/")
        free_gb = free / (1024 ** 3)
        if free_gb > 1:
            return {"status": "healthy", "message": f"{free_gb:.2f} GB فضای خالی", "data": {"free_gb": free_gb}}
        return {"status": "warning", "message": f"فقط {free_gb:.2f} GB فضای خالی", "data": {"free_gb": free_gb}}
    except Exception as e:
        return {"status": "unhealthy", "message": str(e)}


def check_memory():
    try:
        import psutil
        memory = psutil.virtual_memory()
        available_gb = memory.available / (1024 ** 3)
        percent = memory.percent
        if percent < 80:
            return {"status": "healthy", "message": f"{available_gb:.2f} GB حافظه آزاد ({percent}% استفاده)", "data": {"available_gb": available_gb, "percent": percent}}
        return {"status": "warning", "message": f"استفاده از حافظه بالا: {percent}%", "data": {"available_gb": available_gb, "percent": percent}}
    except Exception as e:
        return {"status": "unhealthy", "message": str(e)}


def main():
    logger.info("=" * 60)
    logger.info("🏥 بررسی سلامت سیستم")
    logger.info("=" * 60)

    checks = {
        "دیتابیس": check_database(),
        "Redis": check_redis(),
        "API": check_api(),
        "فضای دیسک": check_disk_space(),
        "حافظه": check_memory()
    }

    all_healthy = True

    for name, result in checks.items():
        status_icon = "✅" if result["status"] == "healthy" else "⚠️" if result["status"] == "warning" else "❌"
        logger.info(f"  {status_icon} {name}: {result['message']}")
        if result["status"] == "unhealthy":
            all_healthy = False

    logger.info("=" * 60)

    if all_healthy:
        logger.info("✅ همه سرویس‌ها سالم هستند")
        sys.exit(0)
    else:
        logger.warning("⚠️ برخی سرویس‌ها مشکل دارند")
        sys.exit(1)


if __name__ == "__main__":
    main()
