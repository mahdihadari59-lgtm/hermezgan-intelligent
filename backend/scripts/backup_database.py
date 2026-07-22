#!/usr/bin/env python
"""
اسکریپت پشتیبان‌گیری از دیتابیس
"""

import sys
import os
from pathlib import Path
import subprocess
import datetime
import gzip
import shutil
import re

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def backup_database(output_dir="backups", compress=True, filename_prefix=None):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    prefix = filename_prefix or settings.APP_NAME.replace(" ", "_")
    filename = f"{prefix}_{timestamp}.sql"
    file_path = output_path / filename

    db_url = settings.DATABASE_URL
    if not db_url.startswith("postgresql://"):
        logger.error("❌ فقط دیتابیس PostgreSQL پشتیبانی می‌شود")
        return None

    pattern = r"postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)"
    match = re.match(pattern, db_url)

    if not match:
        logger.error(f"❌ فرمت DATABASE_URL نامعتبر: {db_url}")
        return None

    user, password, host, port, database = match.groups()
    env = os.environ.copy()
    env["PGPASSWORD"] = password

    cmd = ["pg_dump", "-h", host, "-p", port, "-U", user, "-d", database, "-F", "p", "-v", "-f", str(file_path)]

    try:
        logger.info(f"🔄 شروع پشتیبان‌گیری از دیتابیس: {database}")
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"❌ خطا در پشتیبان‌گیری: {result.stderr}")
            if file_path.exists():
                file_path.unlink()
            return None

        logger.info(f"✅ پشتیبان‌گیری انجام شد: {file_path}")

        if compress:
            gz_path = file_path.with_suffix(".sql.gz")
            with open(file_path, "rb") as f_in:
                with gzip.open(gz_path, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)
            file_path.unlink()
            logger.info(f"✅ فایل فشرده شد: {gz_path}")
            return str(gz_path)

        return str(file_path)

    except FileNotFoundError:
        logger.error("❌ pg_dump یافت نشد. لطفاً PostgreSQL را نصب کنید.")
        return None
    except Exception as e:
        logger.error(f"❌ خطا در پشتیبان‌گیری: {e}")
        return None


def main():
    logger.info("=" * 60)
    logger.info("💾 پشتیبان‌گیری از دیتابیس")
    logger.info("=" * 60)
    backup_file = backup_database()
    if backup_file:
        logger.info(f"📁 فایل پشتیبان: {backup_file}")
        logger.info(f"📊 حجم فایل: {Path(backup_file).stat().st_size / 1024:.2f} KB")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
