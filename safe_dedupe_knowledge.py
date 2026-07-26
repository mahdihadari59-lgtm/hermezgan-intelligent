#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Safe duplicate detector for SQLite knowledge databases.

Goals:
- Never delete data by default.
- Create a review table of likely duplicates.
- Back up the database before any write.
- Use conservative matching so false positives stay low.

Default match policy:
1) normalized(title) matches
2) normalized(category) matches
3) content matches exactly after normalization when a content-like column exists

Usage:
  python3 safe_dedupe_knowledge.py --db backend/hdp_v2.db
  python3 safe_dedupe_knowledge.py --db backend/hdp_v2.db --backup-dir backups --export-csv backups/duplicate_review.csv

Optional:
  python3 safe_dedupe_knowledge.py --db backend/hdp_v2.db --reset-review

This script intentionally does NOT delete from knowledge.
"""

from __future__ import annotations

import argparse
import csv
import sqlite3
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional


CONTENT_CANDIDATES = (
    "content",
    "body",
    "text",
    "description",
    "summary",
    "answer",
    "detail",
    "details",
    "notes",
    "value",
    "value_text",
)


def normalize_expr(column: str) -> str:
    # Lowercase, trim, collapse whitespace, remove common zero-width chars.
    return (
        f"lower(trim(replace(replace(replace("
        f"coalesce({column}, ''), char(8203), ''), char(8204), ''), char(160), ' ')))"
    )


def backup_db(db_path: Path, backup_dir: Path) -> Optional[Path]:
    if not db_path.exists():
        return None
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"{db_path.stem}_{stamp}{db_path.suffix}"
    shutil.copy2(db_path, backup_path)
    return backup_path


def table_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return [row[1] for row in rows]


def detect_content_column(columns: list[str]) -> Optional[str]:
    for candidate in CONTENT_CANDIDATES:
        if candidate in columns:
            return candidate
    return None


def ensure_review_table(conn: sqlite3.Connection, reset: bool = False) -> None:
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
        """
        CREATE UNIQUE INDEX IF NOT EXISTS uq_duplicate_review_pair
        ON duplicate_review(keep_id, duplicate_id)
        """
    )
    if reset:
        conn.execute("DELETE FROM duplicate_review")


def insert_exact_duplicates(
    conn: sqlite3.Connection,
    content_col: Optional[str],
    title_col: str = "title",
    category_col: str = "category",
) -> int:
    # Conservative: only exact normalized title/category, and exact content if available.
    title_norm = normalize_expr(f"k1.{title_col}")
    title_norm2 = normalize_expr(f"k2.{title_col}")
    category_norm = normalize_expr(f"k1.{category_col}")
    category_norm2 = normalize_expr(f"k2.{category_col}")

    where_parts = [
        "k1.id < k2.id",
        f"{title_norm} = {title_norm2}",
        f"{category_norm} = {category_norm2}",
    ]

    if content_col:
        content_norm = normalize_expr(f"k1.{content_col}")
        content_norm2 = normalize_expr(f"k2.{content_col}")
        where_parts.append(f"{content_norm} = {content_norm2}")

    where_sql = " AND ".join(where_parts)

    # Score is intentionally simple: 1.0 for exact matches.
    sql = f"""
        INSERT OR IGNORE INTO duplicate_review (keep_id, duplicate_id, score, status)
        SELECT
            k1.id AS keep_id,
            k2.id AS duplicate_id,
            1.0 AS score,
            'pending' AS status
        FROM knowledge k1
        JOIN knowledge k2
          ON {where_sql}
    """
    cur = conn.execute(sql)
    return cur.rowcount if cur.rowcount != -1 else conn.total_changes


def export_review_csv(conn: sqlite3.Connection, out_path: Path) -> int:
    rows = conn.execute(
        """
        SELECT dr.keep_id, dr.duplicate_id, dr.score, dr.status,
               k1.title AS keep_title, k1.category AS keep_category,
               k2.title AS duplicate_title, k2.category AS duplicate_category
        FROM duplicate_review dr
        LEFT JOIN knowledge k1 ON k1.id = dr.keep_id
        LEFT JOIN knowledge k2 ON k2.id = dr.duplicate_id
        ORDER BY dr.keep_id, dr.duplicate_id
        """
    ).fetchall()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "keep_id",
                "duplicate_id",
                "score",
                "status",
                "keep_title",
                "keep_category",
                "duplicate_title",
                "duplicate_category",
            ]
        )
        writer.writerows(rows)
    return len(rows)


def top_categories(conn: sqlite3.Connection) -> list[tuple[str, int]]:
    return conn.execute(
        """
        SELECT COALESCE(k.category, ''), COUNT(*) AS cnt
        FROM duplicate_review dr
        JOIN knowledge k ON k.id = dr.keep_id
        GROUP BY COALESCE(k.category, '')
        ORDER BY cnt DESC, k.category ASC
        """
    ).fetchall()


def sample_pairs(conn: sqlite3.Connection, limit: int = 20) -> list[tuple]:
    return conn.execute(
        """
        SELECT dr.keep_id, dr.duplicate_id, dr.score,
               k1.title, k1.category
        FROM duplicate_review dr
        JOIN knowledge k1 ON k1.id = dr.keep_id
        ORDER BY dr.keep_id, dr.duplicate_id
        LIMIT ?
        """,
        (limit,),
    ).fetchall()


def main() -> int:
    parser = argparse.ArgumentParser(description="Safe duplicate review generator for SQLite.")
    parser.add_argument("--db", required=True, help="SQLite database path")
    parser.add_argument("--backup-dir", default="backups", help="Directory for DB backups")
    parser.add_argument(
        "--reset-review",
        action="store_true",
        help="Clear duplicate_review before inserting fresh candidates",
    )
    parser.add_argument(
        "--export-csv",
        default=None,
        help="Optional CSV export path for manual review",
    )
    args = parser.parse_args()

    db_path = Path(args.db).expanduser().resolve()
    backup_dir = Path(args.backup_dir).expanduser().resolve()

    if not db_path.exists():
        raise SystemExit(f"Database not found: {db_path}")

    backup_path = backup_db(db_path, backup_dir)

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.execute("PRAGMA journal_mode=WAL;")

    ensure_review_table(conn, reset=args.reset_review)

    columns = table_columns(conn, "knowledge")
    content_col = detect_content_column(columns)

    if "title" not in columns:
        raise SystemExit("knowledge table has no title column")
    if "category" not in columns:
        raise SystemExit("knowledge table has no category column")

    inserted = insert_exact_duplicates(conn, content_col=content_col)
    total = conn.execute("SELECT COUNT(*) FROM duplicate_review").fetchone()[0]

    print(f"Database: {db_path}")
    if backup_path:
        print(f"Backup:   {backup_path}")
    print(f"Content column detected: {content_col or 'none'}")
    print(f"Inserted/updated candidates: {inserted}")
    print(f"Total review rows: {total}")

    print("\nTop categories:")
    for cat, cnt in top_categories(conn)[:20]:
        label = cat if cat else "(empty)"
        print(f"  {label}: {cnt}")

    print("\nSample rows:")
    for keep_id, dup_id, score, title, category in sample_pairs(conn, 20):
        print(f"  keep={keep_id} dup={dup_id} score={score:.2f} | {title} [{category}]")

    if args.export_csv:
        export_path = Path(args.export_csv).expanduser().resolve()
        n = export_review_csv(conn, export_path)
        print(f"\nCSV exported: {export_path} ({n} rows)")

    conn.commit()
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
