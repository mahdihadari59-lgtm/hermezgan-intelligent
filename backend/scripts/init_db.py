#!/usr/bin/env python
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.session import engine, Base
from app.models import chat
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    logger.info("🔄 در حال ایجاد جداول دیتابیس...")
    Base.metadata.create_all(bind=engine)
    logger.info("✅ جداول دیتابیس ایجاد شدند!")

if __name__ == "__main__":
    init_db()
