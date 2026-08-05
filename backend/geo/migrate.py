#!/usr/bin/env python3
"""
migrate.py — create/upgrade geo.db from schema.sql (HDP Phase 1)

Usage:
    python3 migrate.py [--db-path geo.db] [--schema schema.sql]

Pure stdlib (sqlite3 + argparse + pathlib) — matches HDP's dependency policy.
"""
import argparse
import sqlite3
import sys
from pathlib import Path


def check_rtree_available(conn: sqlite3.Connection) -> bool:
    """Verify the SQLite build has the R-Tree virtual table module compiled in."""
    try:
        conn.execute("CREATE VIRTUAL TABLE _rtree_probe USING rtree(id, minX, maxX, minY, maxY)")
        conn.execute("DROP TABLE _rtree_probe")
        return True
    except sqlite3.OperationalError:
        return False


def migrate(db_path: str, schema_path: str) -> None:
    schema_file = Path(schema_path)
    if not schema_file.exists():
        print(f"ERROR: schema file not found: {schema_file}", file=sys.stderr)
        sys.exit(1)

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")

    if not check_rtree_available(conn):
        conn.close()
        print(
            "ERROR: this SQLite build does not have the R-Tree module compiled in.\n"
            "  On Termux:  pkg install sqlite   (the default build includes R-Tree)\n"
            "  On Debian/Ubuntu: apt install sqlite3 libsqlite3-mod-spatialite is NOT needed;\n"
            "  R-Tree ships with mainline SQLite >= 3.8.0 as long as it wasn't built with\n"
            "  SQLITE_OMIT_RTREE. If this still fails, rebuild Python's sqlite3 against a\n"
            "  standard libsqlite3, or fall back to manual bounding-box filtering in\n"
            "  spatial_api.py (slower, no index).",
            file=sys.stderr,
        )
        sys.exit(1)

    with open(schema_file, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()

    tables = [
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type IN ('table','view') "
            "AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )
    ]
    conn.close()

    print(f"OK: {db_path} migrated. {len(tables)} tables/views present:")
    for t in tables:
        print(f"  - {t}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate geo.db for HDP spatial indexing")
    parser.add_argument("--db-path", default="geo.db")
    parser.add_argument("--schema", default="schema.sql")
    args = parser.parse_args()
    migrate(args.db_path, args.schema)
