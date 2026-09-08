#!/usr/bin/env python
"""
اسکریپت پر کردن دیتابیس با داده‌های اولیه
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.core.database import get_db_session
from app.models.user import User
from app.models.location import Service
from app.models.camera import Camera
from app.models.hotspot import Hotspot
from app.models.chat import ChatIntent, ChatEntity
from app.core.security import hash_password
from app.core.constants import REGIONS, SERVICE_TYPES, CAMERA_TYPES, HOTSPOT_TYPES
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_users(db: Session):
    logger.info("👤 Seeding users...")
    users = [
        {"username": "admin", "email": "admin@hermezgan.ir", "full_name": "مدیر سیستم", "is_active": True, "is_verified": True, "is_admin": True},
        {"username": "moderator", "email": "moderator@hermezgan.ir", "full_name": "ناظر سیستم", "is_active": True, "is_verified": True, "is_admin": False},
        {"username": "user1", "email": "user1@example.com", "full_name": "کاربر یک", "is_active": True, "is_verified": True, "is_admin": False},
        {"username": "user2", "email": "user2@example.com", "full_name": "کاربر دو", "is_active": True, "is_verified": False, "is_admin": False}
    ]
    for user_data in users:
        existing = db.query(User).filter(User.username == user_data["username"]).first()
        if existing:
            logger.info(f"  ⏭️  کاربر {user_data['username']} قبلاً وجود دارد")
            continue
        user = User(**user_data)
        user.set_password("SecurePass123!")
        db.add(user)
    db.commit()
    logger.info(f"✅ {len(users)} کاربر اضافه شد")


def seed_services(db: Session):
    logger.info("🏥 Seeding services...")
    services = [
        {"name": "بیمارستان امام خمینی", "type": "hospital", "latitude": 27.2158, "longitude": 56.2808, "address": "بندرعباس، خیابان شهید رجایی", "phone": "076-3400123", "rating": 4.8, "status": "active"},
        {"name": "بیمارستان فوق تخصصی کودکان", "type": "hospital", "latitude": 27.2200, "longitude": 56.2850, "address": "بندرعباس، خیابان ولیعصر", "phone": "076-3400456", "rating": 4.9, "status": "active"},
        {"name": "رستوران تالار خلیج", "type": "restaurant", "latitude": 27.2220, "longitude": 56.2900, "address": "بندرعباس، بلوار ساحلی", "phone": "076-3222222", "rating": 4.5, "status": "active"},
        {"name": "رستوران دریای آبی", "type": "restaurant", "latitude": 27.2100, "longitude": 56.2750, "address": "بندرعباس، خیابان تجریش", "phone": "076-3222333", "rating": 4.3, "status": "active"},
        {"name": "تاکسی آنلاین الفردوس", "type": "taxi", "latitude": 27.2250, "longitude": 56.2700, "address": "بندرعباس، ایستگاه تاکسی مرکزی", "phone": "076-91111111", "rating": 4.6, "status": "active"},
        {"name": "داروخانه شفابخش", "type": "pharmacy", "latitude": 27.2180, "longitude": 56.2780, "address": "بندرعباس، خیابان شریعتی", "phone": "076-3111111", "rating": 4.4, "status": "active"},
        {"name": "مدرسه فرزانگان", "type": "school", "latitude": 27.2300, "longitude": 56.2950, "address": "بندرعباس، خیابان دانشگاه", "phone": "076-3333333", "rating": 4.7, "status": "active"}
    ]
    for service_data in services:
        existing = db.query(Service).filter(Service.name == service_data["name"], Service.type == service_data["type"]).first()
        if existing:
            logger.info(f"  ⏭️  سرویس {service_data['name']} قبلاً وجود دارد")
            continue
        service = Service(**service_data)
        db.add(service)
    db.commit()
    logger.info(f"✅ {len(services)} سرویس اضافه شد")


def seed_cameras(db: Session):
    logger.info("📹 Seeding cameras...")
    cameras = [
        {"camera_id": "CAM-001", "name": "چهارراه غزی", "region": "bandar-abbas", "latitude": 27.2158, "longitude": 56.2808, "types": ["traffic-light", "speed"], "status": "active", "priority": "high"},
        {"camera_id": "CAM-002", "name": "میدان سپاه", "region": "bandar-abbas", "latitude": 27.2200, "longitude": 56.2850, "types": ["traffic-light"], "status": "active", "priority": "normal"},
        {"camera_id": "CAM-003", "name": "بلوار امام خمینی", "region": "bandar-abbas", "latitude": 27.2180, "longitude": 56.2750, "types": ["speed"], "status": "active", "priority": "high"},
        {"camera_id": "CAM-004", "name": "پل خواجو", "region": "bandar-abbas", "latitude": 27.2250, "longitude": 56.2900, "types": ["speed", "plate"], "status": "installing", "priority": "normal"},
        {"camera_id": "CAM-005", "name": "بلوار هرمز", "region": "bandar-abbas", "latitude": 27.2100, "longitude": 56.2700, "types": ["speed", "night-ir"], "status": "pending", "priority": "urgent"},
        {"camera_id": "CAM-006", "name": "بلوار ساحلی قشم", "region": "qeshm", "latitude": 26.9500, "longitude": 55.4700, "types": ["speed"], "status": "active", "priority": "normal"},
        {"camera_id": "CAM-007", "name": "اسکله قشم", "region": "qeshm", "latitude": 26.9400, "longitude": 55.4600, "types": ["surveillance", "face-recognition"], "status": "active", "priority": "high"}
    ]
    for camera_data in cameras:
        existing = db.query(Camera).filter(Camera.camera_id == camera_data["camera_id"]).first()
        if existing:
            logger.info(f"  ⏭️  دوربین {camera_data['camera_id']} قبلاً وجود دارد")
            continue
        camera = Camera(**camera_data)
        db.add(camera)
    db.commit()
    logger.info(f"✅ {len(cameras)} دوربین اضافه شد")


def seed_hotspots(db: Session):
    logger.info("🚨 Seeding hotspots...")
    hotspots = [
        {"type": "accident", "latitude": 27.2200, "longitude": 56.2850, "title": "تصادف در تقاطع خیابان شهید رجایی", "description": "تصادف بین دو خودرو - ترافیک سنگین", "severity": "high", "status": "active", "reported_by": "سیستم"},
        {"type": "traffic", "latitude": 27.2180, "longitude": 56.2750, "title": "ترافیک سنگین خیابان ولیعصر", "description": "ترافیک بسیار سنگین - از جمهوری تا شهید رجایی", "severity": "medium", "status": "active", "reported_by": "سیستم ترافیکی"},
        {"type": "danger", "latitude": 27.2250, "longitude": 56.2900, "title": "منطقه خطرناک - عدم رعایت علائم", "description": "منطقه‌ای که رانندگان سرعت را رعایت نمی‌کنند", "severity": "high", "status": "active", "reported_by": "پلیس راهور"},
        {"type": "construction", "latitude": 27.2100, "longitude": 56.2800, "title": "ساخت و ساز خیابان تجریش", "description": "ساخت و ساز جاده - دو خط مسدود", "severity": "low", "status": "active", "reported_by": "شهرداری"}
    ]
    for hotspot_data in hotspots:
        hotspot = Hotspot(**hotspot_data)
        db.add(hotspot)
    db.commit()
    logger.info(f"✅ {len(hotspots)} نقطه حادثه‌خیز اضافه شد")


def seed_chat_intents(db: Session):
    logger.info("💬 Seeding chat intents...")
    intents = [
        {"name": "hospital", "keywords": ["بیمارستان", "بیمار", "درمان", "داکتر", "دکتر", "پزشک", "اورژانس"], "response_template": "نزدیک‌ترین بیمارستان‌ها:", "entity_type": "service", "is_active": True},
        {"name": "restaurant", "keywords": ["رستوران", "غذا", "کباب", "شام", "ناهار", "فست فود", "پیتزا"], "response_template": "رستوران‌های نزدیک:", "entity_type": "service", "is_active": True},
        {"name": "taxi", "keywords": ["تاکسی", "خودرو", "رفتن", "حمل", "مسافر", "سوار", "پیاده"], "response_template": "تاکسی‌های در دسترس:", "entity_type": "service", "is_active": True},
        {"name": "camera", "keywords": ["دوربین", "نظارتی", "تخلف", "سرعت", "ترافیک", "ثبت", "پلاک"], "response_template": "دوربین‌های نظارتی منطقه:", "entity_type": "camera", "is_active": True},
        {"name": "hotspot", "keywords": ["حادثه", "خطرناک", "تصادف", "خطر", "حادثه‌خیز", "مشکل", "بحران"], "response_template": "نقاط حادثه‌خیز نزدیک:", "entity_type": "hotspot", "is_active": True},
        {"name": "location", "keywords": ["موقعیت", "مکان", "کجا", "آدرس", "نزدیک", "دور", "فاصله"], "response_template": "موقعیت شما:", "entity_type": "location", "is_active": True},
        {"name": "general", "keywords": ["سلام", "خوب", "ممنون", "مرسی", "بله", "خیر", "نه"], "response_template": "چطور می‌تونم کمکتون کنم؟", "entity_type": "general", "is_active": True}
    ]
    for intent_data in intents:
        existing = db.query(ChatIntent).filter(ChatIntent.name == intent_data["name"]).first()
        if existing:
            logger.info(f"  ⏭️  نیت {intent_data['name']} قبلاً وجود دارد")
            continue
        intent = ChatIntent(**intent_data)
        db.add(intent)
    db.commit()
    logger.info(f"✅ {len(intents)} نیت اضافه شد")


def seed_chat_entities(db: Session):
    logger.info("🔍 Seeding chat entities...")
    entities = [
        {"name": "بندرعباس", "entity_type": "region", "synonyms": ["بندرعباس", "بندر", "مرکز استان"], "metadata": {"lat": 27.2158, "lng": 56.2808}},
        {"name": "قشم", "entity_type": "region", "synonyms": ["قشم", "جزیره قشم"], "metadata": {"lat": 26.9500, "lng": 55.4700}},
        {"name": "کیش", "entity_type": "region", "synonyms": ["کیش", "جزیره کیش"], "metadata": {"lat": 26.5200, "lng": 53.9800}},
        {"name": "هرمز", "entity_type": "region", "synonyms": ["هرمز", "جزیره هرمز"], "metadata": {"lat": 27.0800, "lng": 56.4500}},
        {"name": "بیمارستان", "entity_type": "service", "synonyms": ["بیمارستان", "درمانگاه", "مرکز درمانی"], "metadata": {"type": "hospital"}},
        {"name": "رستوران", "entity_type": "service", "synonyms": ["رستوران", "کبابی", "فست فود"], "metadata": {"type": "restaurant"}},
        {"name": "تاکسی", "entity_type": "service", "synonyms": ["تاکسی", "اسنپ", "تپسی"], "metadata": {"type": "taxi"}}
    ]
    for entity_data in entities:
        existing = db.query(ChatEntity).filter(ChatEntity.name == entity_data["name"]).first()
        if existing:
            logger.info(f"  ⏭️  موجودیت {entity_data['name']} قبلاً وجود دارد")
            continue
        entity = ChatEntity(**entity_data)
        db.add(entity)
    db.commit()
    logger.info(f"✅ {len(entities)} موجودیت اضافه شد")


def main():
    logger.info("=" * 60)
    logger.info("🌱 شروع پر کردن دیتابیس با داده‌های اولیه")
    logger.info("=" * 60)
    db = get_db_session()
    try:
        seed_users(db)
        seed_services(db)
        seed_cameras(db)
        seed_hotspots(db)
        seed_chat_intents(db)
        seed_chat_entities(db)
        logger.info("=" * 60)
        logger.info("✅ دیتابیس با موفقیت پر شد!")
        logger.info("=" * 60)
    except Exception as e:
        logger.error(f"❌ خطا در پر کردن دیتابیس: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
