#!/usr/bin/env python
"""
اسکریپت پاکسازی فایل‌های موقت و کش
"""

import sys
import os
from pathlib import Path
import shutil
import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def cleanup_temp_files(temp_dir="temp", max_age_days=7, dry_run=False):
    temp_path = Path(temp_dir)

    if not temp_path.exists():
        logger.info(f"ℹ️  پوشه {temp_dir} وجود ندارد")
        return {"deleted_files": 0, "deleted_size": 0, "errors": 0}

    now = datetime.datetime.utcnow()
    stats = {"deleted_files": 0, "deleted_size": 0, "errors": 0}

    for item in temp_path.rglob("*"):
        if item.is_file():
            mtime = datetime.datetime.fromtimestamp(item.stat().st_mtime)
            age_days = (now - mtime).days

            if age_days > max_age_days:
                file_size = item.stat().st_size
                logger.info(f"  🗑️  {item} ({file_size} bytes, {age_days} روز)")

                if not dry_run:
                    try:
                        item.unlink()
                        stats["deleted_files"] += 1
                        stats["deleted_size"] += file_size
                    except Exception as e:
                        logger.error(f"  ❌ خطا در حذف {item}: {e}")
                        stats["errors"] += 1

    if not dry_run:
        for item in sorted(temp_path.rglob("*"), reverse=True):
            if item.is_dir() and not any(item.iterdir()):
                try:
                    item.rmdir()
                    logger.info(f"  🗑️  پوشه خالی حذف شد: {item}")
                except Exception:
                    pass

    logger.info(f"✅ {stats['deleted_files']} فایل با حجم {stats['deleted_size'] / 1024:.2f} KB حذف شد")
    return stats


def cleanup_old_logs(log_dir="logs", max_age_days=30, dry_run=False):
    log_path = Path(log_dir)

    if not log_path.exists():
        logger.info(f"ℹ️  پوشه {log_dir} وجود ندارد")
        return {"deleted_files": 0, "deleted_size": 0}

    now = datetime.datetime.utcnow()
    stats = {"deleted_files": 0, "deleted_size": 0}

    for item in log_path.glob("*.log*"):
        if item.is_file():
            mtime = datetime.datetime.fromtimestamp(item.stat().st_mtime)
            age_days = (now - mtime).days

            if age_days > max_age_days:
                file_size = item.stat().st_size
                logger.info(f"  🗑️  {item} ({file_size} bytes, {age_days} روز)")

                if not dry_run:
                    try:
                        item.unlink()
                        stats["deleted_files"] += 1
                        stats["deleted_size"] += file_size
                    except Exception as e:
                        logger.error(f"  ❌ خطا در حذف {item}: {e}")

    logger.info(f"✅ {stats['deleted_files']} فایل لاگ با حجم {stats['deleted_size'] / 1024:.2f} KB حذف شد")
    return stats


def cleanup_old_backups(backup_dir="backups", max_age_days=30, keep_min=5, dry_run=False):
    backup_path = Path(backup_dir)

    if not backup_path.exists():
        logger.info(f"ℹ️  پوشه {backup_dir} وجود ندارد")
        return {"deleted_files": 0, "deleted_size": 0}

    backup_files = []
    for item in backup_path.glob("*.sql*"):
        if item.is_file():
            backup_files.append({"path": item, "mtime": item.stat().st_mtime, "size": item.stat().st_size})

    backup_files.sort(key=lambda x: x["mtime"], reverse=True)

    to_delete = backup_files[keep_min:]

    now = datetime.datetime.utcnow()
    stats = {"deleted_files": 0, "deleted_size": 0}

    for item in to_delete:
        mtime = datetime.datetime.fromtimestamp(item["mtime"])
        age_days = (now - mtime).days

        if age_days > max_age_days:
            logger.info(f"  🗑️  {item['path']} ({item['size']} bytes, {age_days} روز)")

            if not dry_run:
                try:
                    item["path"].unlink()
                    stats["deleted_files"] += 1
                    stats["deleted_size"] += item["size"]
                except Exception as e:
                    logger.error(f"  ❌ خطا در حذف {item['path']}: {e}")

    logger.info(f"✅ {stats['deleted_files']} فایل پشتیبان با حجم {stats['deleted_size'] / 1024:.2f} KB حذف شد")
    return stats


def main():
    logger.info("=" * 60)
    logger.info("🧹 پاکسازی فایل‌های موقت و کش")
    logger.info("=" * 60)

    dry_run = "--dry-run" in sys.argv

    if dry_run:
        logger.info("ℹ️  حالت Dry Run - فقط نمایش بدون حذف")

    logger.info("\n📁 پاکسازی فایل‌های موقت:")
    cleanup_temp_files(dry_run=dry_run)

    logger.info("\n📁 پاکسازی لاگ‌های قدیمی:")
    cleanup_old_logs(dry_run=dry_run)

    logger.info("\n📁 پاکسازی پشتیبان‌های قدیمی:")
    cleanup_old_backups(dry_run=dry_run)

    logger.info("\n✅ پاکسازی کامل شد!")


if __name__ == "__main__":
    main()
