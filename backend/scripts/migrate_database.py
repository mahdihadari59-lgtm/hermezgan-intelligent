#!/usr/bin/env python
"""
اسکریپت اجرای مهاجرت‌های دیتابیس
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database.migrations import MigrationManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    logger.info("=" * 60)
    logger.info("🔄 شروع اجرای مهاجرت‌های دیتابیس")
    logger.info("=" * 60)

    manager = MigrationManager()
    migrations = manager.get_migrations()

    if not migrations:
        logger.info("ℹ️  هیچ مهاجرتی برای اجرا وجود ندارد")
        return

    logger.info(f"📋 {len(migrations)} مهاجرت یافت شد")

    executed = 0
    for migration in migrations:
        logger.info(f"  ▶️  اجرای: {migration['filename']}")
        if manager.run_migration(migration["filename"]):
            executed += 1
            logger.info(f"  ✅ {migration['filename']} با موفقیت اجرا شد")
        else:
            logger.error(f"  ❌ خطا در اجرای {migration['filename']}")
            sys.exit(1)

    logger.info("=" * 60)
    logger.info(f"✅ {executed} مهاجرت با موفقیت اجرا شد")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
