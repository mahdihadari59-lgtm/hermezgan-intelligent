#!/usr/bin/env python
"""
اسکریپت بازیابی دیتابیس از پشتیبان
"""

import sys
import os
from pathlib import Path
import subprocess
import gzip
import re

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def restore_database(backup_file):
    backup_path = Path(backup_file)

    if not backup_path.exists():
        logger.error(f"❌ فایل پشتیبان یافت نشد: {backup_file}")
        return False

    if backup_path.suffix == ".gz":
        logger.info("📦 فایل فشرده است، در حال خارج‌سازی...")
        sql_path = backup_path.with_suffix("")
        with gzip.open(backup_path, "rb") as f_in:
            with open(sql_path, "wb") as f_out:
                f_out.write(f_in.read())
        restore_file = sql_path
        cleanup = True
    else:
        restore_file = backup_path
        cleanup = False

    db_url = settings.DATABASE_URL
    if not db_url.startswith("postgresql://"):
        logger.error("❌ فقط دیتابیس PostgreSQL پشتیبانی می‌شود")
        return False

    pattern = r"postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)"
    match = re.match(pattern, db_url)

    if not match:
        logger.error(f"❌ فرمت DATABASE_URL نامعتبر: {db_url}")
        return False

    user, password, host, port, database = match.groups()

    confirm = input(f"⚠️  آیا از بازیابی دیتابیس '{database}' اطمینان دارید؟ (yes/no): ")
    if confirm.lower() != "yes":
        logger.info("❌ عملیات لغو شد")
        return False

    env = os.environ.copy()
    env["PGPASSWORD"] = password

    cmd = ["psql", "-h", host, "-p", port, "-U", user, "-d", database, "-f", str(restore_file)]

    try:
        logger.info(f"🔄 شروع بازیابی دیتابیس: {database}")
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"❌ خطا در بازیابی: {result.stderr}")
            return False

        logger.info("✅ دیتابیس با موفقیت بازیابی شد")

        if cleanup and restore_file.exists():
            restore_file.unlink()
            logger.info("🗑️ فایل موقت حذف شد")

        return True

    except FileNotFoundError:
        logger.error("❌ psql یافت نشد. لطفاً PostgreSQL را نصب کنید.")
        return False
    except Exception as e:
        logger.error(f"❌ خطا در بازیابی: {e}")
        return False


def main():
    logger.info("=" * 60)
    logger.info("🔄 بازیابی دیتابیس از پشتیبان")
    logger.info("=" * 60)

    if len(sys.argv) < 2:
        logger.error("❌ مسیر فایل پشتیبان را وارد کنید:")
        logger.info("  python scripts/restore_database.py backups/hermezgan_20240101_120000.sql.gz")
        sys.exit(1)

    backup_file = sys.argv[1]
    success = restore_database(backup_file)

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
