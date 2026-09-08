#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import candidate duplicate pairs from a CSV into the duplicate_review table
of hdp_v2.db, so they can then be processed by merge_duplicate_knowledge_v2.py.

Expected CSV columns (header row required):
  keep_id, duplicate_id, score, status, keep_title, keep_category,
  duplicate_title, duplicate_category

Behavior:
- always creates a backup of the db before touching it
- creates the duplicate_review table if it doesn't exist yet
  (with a UNIQUE(keep_id, duplicate_id) constraint so re-imports are safe)
- skips rows whose keep_id or duplicate_id doesn't exist in `knowledge`
  (reports them instead of silently inserting a broken reference)
- skips rows that already exist in duplicate_review (won't overwrite an
  existing status like 'approved' or 'merged')
- default mode is dry-run; pass --apply to actually write

Usage:
  python3 import_duplicate_review.py --db backend/hdp_v2.db --csv duplicate_review.csv
  python3 import_duplicate_review.py --db backend/hdp_v2.db --csv duplicate_review.csv --apply
"""

from __future__ import annotations

import argparse
import csv
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path


REQUIRED_COLS = [
    "keep_id", "duplicate_id", "score", "status",
    "keep_title", "keep_category", "duplicate_title", "duplicate_category",
]


def backup_db(db_path: Path, backup_dir: Path) -> Path:
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = backup_dir / f"{db_path.stem}_{stamp}{db_path.suffix}"
    shutil.copy2(db_path, out)
    return out


def ensure_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS duplicate_review (
            keep_id INTEGER,
            duplicate_id INTEGER,
            score REAL,
            status TEXT DEFAULT 'pending'
        )
        """
    )
    conn.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_duplicate_review_pair "
        "ON duplicate_review(keep_id, duplicate_id)"
    )


def table_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    return [row[1] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()]


def load_csv(path: Path) -> list[dict[str, str]]:
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED_COLS if c not in (reader.fieldnames or [])]
        if missing:
            raise SystemExit(f"CSV is missing required columns: {missing}")
        return list(reader)


def existing_knowledge_ids(conn: sqlite3.Connection) -> set[int]:
    return {row[0] for row in conn.execute("SELECT id FROM knowledge").fetchall()}


def existing_pairs(conn: sqlite3.Connection) -> set[tuple[int, int]]:
    return {
        (row[0], row[1])
        for row in conn.execute("SELECT keep_id, duplicate_id FROM duplicate_review").fetchall()
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Import duplicate_review.csv into hdp_v2.db")
    p.add_argument("--db", required=True, help="SQLite database path")
    p.add_argument("--csv", required=True, help="Path to duplicate_review.csv")
    p.add_argument("--backup-dir", default="backups", help="Backup directory")
    p.add_argument("--apply", action="store_true", help="Apply changes (default: dry-run)")
    args = p.parse_args()

    db_path = Path(args.db).expanduser().resolve()
    csv_path = Path(args.csv).expanduser().resolve()
    if not db_path.exists():
        raise SystemExit(f"Database not found: {db_path}")
    if not csv_path.exists():
        raise SystemExit(f"CSV not found: {csv_path}")

    rows = load_csv(csv_path)
    print(f"CSV rows loaded: {len(rows)}")

    if args.apply:
        backup_path = backup_db(db_path, Path(args.backup_dir).expanduser().resolve())
        print(f"Backup created: {backup_path}")

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys=ON;")

    ensure_table(conn)

    known_ids = existing_knowledge_ids(conn)
    known_pairs = existing_pairs(conn)

    to_insert: list[tuple] = []
    skipped_existing = 0
    skipped_missing_ref: list[dict[str, str]] = []

    for r in rows:
        try:
            keep_id = int(r["keep_id"])
            dup_id = int(r["duplicate_id"])
            score = float(r["score"]) if r["score"] not in (None, "") else None
        except ValueError:
            skipped_missing_ref.append(r)
            continue

        if (keep_id, dup_id) in known_pairs:
            skipped_existing += 1
            continue

        if keep_id not in known_ids or dup_id not in known_ids:
            skipped_missing_ref.append(r)
            continue

        to_insert.append((keep_id, dup_id, score, r.get("status") or "pending"))

    print(f"New pairs to insert:        {len(to_insert)}")
    print(f"Already in duplicate_review: {skipped_existing}")
    print(f"Skipped (bad/missing ref):   {len(skipped_missing_ref)}")

    if skipped_missing_ref:
        print("\nFirst few skipped rows (keep_id/duplicate_id not found in `knowledge`):")
        for r in skipped_missing_ref[:10]:
            print(f"  keep_id={r.get('keep_id')} duplicate_id={r.get('duplicate_id')} title={r.get('keep_title')}")

    if args.apply:
        cols = table_columns(conn, "duplicate_review")
        base_cols = [c for c in ("keep_id", "duplicate_id", "score", "status") if c in cols]
        placeholders = ", ".join("?" for _ in base_cols)
        conn.executemany(
            f"INSERT INTO duplicate_review ({', '.join(base_cols)}) VALUES ({placeholders})",
            to_insert,
        )
        conn.commit()
        print(f"\nInserted {len(to_insert)} rows into duplicate_review.")
    else:
        print("\nDRY-RUN: no changes written. Re-run with --apply to insert.")

    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
