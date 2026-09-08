#!/usr/bin/env python
"""
اسکریپت ایجاد کاربر ادمین
"""

import sys
import os
from pathlib import Path
import getpass

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import get_db_session
from app.models.user import User
from app.core.security import hash_password
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_admin_user(username=None, email=None, password=None, full_name=None):
    db = get_db_session()
    try:
        if not username:
            username = input("👤 نام کاربری: ").strip()
        if not email:
            email = input("📧 ایمیل: ").strip()
        if not password:
            password = getpass.getpass("🔑 رمز عبور: ").strip()
            confirm = getpass.getpass("🔑 تکرار رمز عبور: ").strip()
            if password != confirm:
                logger.error("❌ رمز عبور و تکرار آن مطابقت ندارند")
                return False
        if not full_name:
            full_name = input("👤 نام کامل: ").strip() or "مدیر سیستم"

        existing = db.query(User).filter((User.username == username) | (User.email == email)).first()
        if existing:
            logger.error(f"❌ کاربر با نام کاربری یا ایمیل '{username}' قبلاً وجود دارد")
            return False

        user = User(username=username, email=email, full_name=full_name, is_active=True, is_verified=True, is_admin=True)
        user.set_password(password)
        db.add(user)
        db.commit()
        db.refresh(user)

        logger.info("=" * 60)
        logger.info("✅ کاربر ادمین با موفقیت ایجاد شد!")
        logger.info("=" * 60)
        logger.info(f"👤 نام کاربری: {user.username}")
        logger.info(f"📧 ایمیل: {user.email}")
        logger.info(f"👤 نام کامل: {user.full_name}")
        logger.info("=" * 60)
        return True

    except Exception as e:
        logger.error(f"❌ خطا در ایجاد کاربر ادمین: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def main():
    logger.info("=" * 60)
    logger.info("👑 ایجاد کاربر ادمین")
    logger.info("=" * 60)
    success = create_admin_user()
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
