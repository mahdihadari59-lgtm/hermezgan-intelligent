from pathlib import Path
import re
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.core.database.session import get_db_session_manager

logger = logging.getLogger(__name__)


class MigrationManager:
    """
    مدیریت مهاجرت‌های دیتابیس
    """

    def __init__(self, migrations_dir: str = "database/migrations"):
        self.migrations_dir = Path(migrations_dir)
        self.migrations_dir.mkdir(parents=True, exist_ok=True)
        self.manager = get_db_session_manager()

    def create_migration(self, name: str, description: str = "") -> str:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{name}.sql"
        file_path = self.migrations_dir / filename

        content = f"""-- ============================================================
-- Migration: {name}
-- Created at: {datetime.utcnow().isoformat()}
-- Description: {description}
-- ============================================================

-- ============================================================
-- UP Migration
-- ============================================================

-- Add your UP migration SQL here


-- ============================================================
-- DOWN Migration (Rollback)
-- ============================================================

-- Add your DOWN migration SQL here
-- WARNING: This will rollback the changes!

"""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"📝 Migration created: {file_path}")
        return str(file_path)

    def get_migrations(self) -> List[Dict[str, Any]]:
        migrations = []

        for file_path in sorted(self.migrations_dir.glob("*.sql")):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            description = ""
            match = re.search(r'-- Description: (.+)', content)
            if match:
                description = match.group(1)

            migrations.append({
                "filename": file_path.name,
                "path": str(file_path),
                "name": file_path.stem.split("_", 1)[-1] if "_" in file_path.stem else file_path.stem,
                "timestamp": file_path.stem.split("_")[0] if "_" in file_path.stem else "",
                "description": description,
                "size": file_path.stat().st_size,
                "created_at": datetime.fromtimestamp(file_path.stat().st_ctime).isoformat()
            })

        return migrations

    def run_migration(self, migration_file: str) -> bool:
        file_path = self.migrations_dir / migration_file

        if not file_path.exists():
            logger.error(f"❌ Migration file not found: {migration_file}")
            return False

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        up_match = re.search(r'-- ============================================================\s*-- UP Migration\s*-- ============================================================\s*(.+?)(?=-- ============================================================|$)', content, re.DOTALL)

        if not up_match:
            logger.error(f"❌ No UP migration section found in: {migration_file}")
            return False

        up_sql = up_match.group(1).strip()

        if not up_sql:
            logger.warning(f"⚠️ UP migration is empty: {migration_file}")
            return True

        try:
            with self.manager.engine.connect() as conn:
                conn.execute(text(up_sql))
                conn.commit()

            logger.info(f"✅ Migration executed: {migration_file}")
            return True

        except Exception as e:
            logger.error(f"❌ Error executing migration: {e}")
            return False

    def rollback_migration(self, migration_file: str) -> bool:
        file_path = self.migrations_dir / migration_file

        if not file_path.exists():
            logger.error(f"❌ Migration file not found: {migration_file}")
            return False

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        down_match = re.search(r'-- ============================================================\s*-- DOWN Migration \(Rollback\)\s*-- ============================================================\s*(.+?)(?=-- ============================================================|$)', content, re.DOTALL)

        if not down_match:
            logger.warning(f"⚠️ No DOWN migration section found in: {migration_file}")
            return True

        down_sql = down_match.group(1).strip()

        if not down_sql:
            logger.warning(f"⚠️ DOWN migration is empty: {migration_file}")
            return True

        try:
            with self.manager.engine.connect() as conn:
                conn.execute(text(down_sql))
                conn.commit()

            logger.info(f"✅ Migration rolled back: {migration_file}")
            return True

        except Exception as e:
            logger.error(f"❌ Error rolling back migration: {e}")
            return False


_migration_manager = None


def get_migration_manager() -> MigrationManager:
    global _migration_manager
    if _migration_manager is None:
        _migration_manager = MigrationManager()
    return _migration_manager


def run_migrations() -> int:
    manager = get_migration_manager()
    migrations = manager.get_migrations()

    executed = 0
    for migration in migrations:
        if manager.run_migration(migration["filename"]):
            executed += 1

    return executed
