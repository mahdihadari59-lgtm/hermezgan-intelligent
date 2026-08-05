#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Safe merge for duplicate knowledge rows in SQLite.

Fixes the earlier UNIQUE constraint failure by handling tables that have a
unique constraint on the knowledge FK column (for example knowledge_stats).

Behavior:
- always creates a backup
- loads duplicate_review rows
- only processes conservative duplicate pairs
- merges content into knowledge without losing text
- updates FK references where safe
- for tables with a UNIQUE FK -> knowledge(id), merges row data instead of
  blindly UPDATEing the FK to a duplicate value
- deletes the duplicate row only after safe merge
- default mode is dry-run

Usage:
  python3 merge_duplicate_knowledge_v2.py --db backend/hdp_v2.db
  python3 merge_duplicate_knowledge_v2.py --db backend/hdp_v2.db --apply --auto-approve
  python3 merge_duplicate_knowledge_v2.py --db backend/hdp_v2.db --apply --approved-only

Notes:
- This is conservative.
- It does not touch tables without a declared FK to knowledge(id).
- It does not assume that all duplicate_review rows are safe unless they pass
  the conservative content/title/category checks.
"""

from __future__ import annotations

import argparse
import shutil
import sqlite3
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Iterable, Optional


ZERO_WIDTH = ("\u200b", "\u200c", "\u200d", "\ufeff")


def norm_text(s: str | None) -> str:
    if not s:
        return ""
    out = s
    for ch in ZERO_WIDTH:
        out = out.replace(ch, "")
    out = out.replace("\u00a0", " ")
    out = " ".join(out.split())
    return out.strip().lower()


def similarity(a: str | None, b: str | None) -> float:
    return SequenceMatcher(None, norm_text(a), norm_text(b)).ratio()


def backup_db(db_path: Path, backup_dir: Path) -> Path:
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = backup_dir / f"{db_path.stem}_{stamp}{db_path.suffix}"
    shutil.copy2(db_path, out)
    return out


def table_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return [r[1] for r in rows]


def table_pk_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    cols = [r[1] for r in rows if r[5] > 0]
    cols.sort(key=lambda c: next(r[5] for r in rows if r[1] == c))
    return cols


def detect_content_column(columns: list[str]) -> Optional[str]:
    candidates = (
        "content",
        "body",
        "text",
        "description",
        "summary",
        "answer",
        "detail",
        "details",
        "notes",
        "value_text",
        "value",
    )
    for name in candidates:
        if name in columns:
            return name
    return None


def split_blocks(text: str) -> list[str]:
    text = text.strip()
    if not text:
        return []
    blocks: list[str] = []
    for raw_para in text.split("\n\n"):
        para = raw_para.strip()
        if not para:
            continue
        lines = [ln.strip() for ln in para.splitlines() if ln.strip()]
        if len(lines) == 1:
            blocks.append(lines[0])
        else:
            blocks.extend(lines)
    return blocks


def merge_text(a: str | None, b: str | None) -> str:
    ta = (a or "").strip()
    tb = (b or "").strip()
    if not ta:
        return tb
    if not tb:
        return ta

    na = norm_text(ta)
    nb = norm_text(tb)

    if na == nb:
        return ta if len(ta) >= len(tb) else tb
    if na and na in nb:
        return tb
    if nb and nb in na:
        return ta

    blocks: list[str] = []
    seen: set[str] = set()
    for source in (ta, tb):
        for block in split_blocks(source):
            key = norm_text(block)
            if key and key not in seen:
                seen.add(key)
                blocks.append(block)

    return "\n\n".join(blocks).strip() or (ta if len(ta) >= len(tb) else tb)


def eligible_pair(
    keep_title: str | None,
    dup_title: str | None,
    keep_cat: str | None,
    dup_cat: str | None,
    keep_content: str | None,
    dup_content: str | None,
) -> bool:
    if norm_text(keep_title) != norm_text(dup_title):
        return False
    if norm_text(keep_cat) != norm_text(dup_cat):
        return False

    ka = norm_text(keep_content)
    db = norm_text(dup_content)
    if not ka or not db:
        return False
    if ka == db:
        return True
    if ka in db or db in ka:
        return True
    if len(db) >= len(ka) and similarity(ka, db) >= 0.55:
        return True
    return False


def fk_targets(conn: sqlite3.Connection, target_table: str = "knowledge") -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    tables = [
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        ).fetchall()
    ]
    for table in tables:
        fks = conn.execute(f"PRAGMA foreign_key_list({table})").fetchall()
        cols: list[str] = []
        for fk in fks:
            # id, seq, table, from, to, on_update, on_delete, match
            if fk[2] == target_table and fk[4] == "id":
                cols.append(fk[3])
        if cols:
            out[table] = cols
    return out


def unique_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    uniques: set[str] = set(table_pk_columns(conn, table))
    idxs = conn.execute(f"PRAGMA index_list({table})").fetchall()
    for idx in idxs:
        idx_name = idx[1]
        is_unique = bool(idx[2])
        if not is_unique:
            continue
        cols = conn.execute(f"PRAGMA index_info({idx_name})").fetchall()
        if len(cols) == 1:
            uniques.add(cols[0][2])
    return uniques


def row_by_fk(conn: sqlite3.Connection, table: str, fk_col: str, fk_value: int) -> Optional[dict[str, object]]:
    cols = table_columns(conn, table)
    cur = conn.execute(f"SELECT * FROM {table} WHERE {fk_col}=?", (fk_value,))
    row = cur.fetchone()
    if not row:
        return None
    return {cols[i]: row[i] for i in range(len(cols))}


def merge_row_dicts(
    keep: dict[str, object],
    dup: dict[str, object],
    *,
    fk_col: str,
    pk_cols: set[str],
) -> dict[str, object]:
    out = dict(keep)
    for key, dup_val in dup.items():
        if key == fk_col or key in pk_cols:
            continue
        keep_val = out.get(key)
        if keep_val is None:
            out[key] = dup_val
            continue
        if isinstance(keep_val, str) or isinstance(dup_val, str):
            out[key] = merge_text(
                str(keep_val) if keep_val is not None else "",
                str(dup_val) if dup_val is not None else "",
            )
            continue
        if keep_val in (None, "") and dup_val not in (None, ""):
            out[key] = dup_val
    return out


def update_row(conn: sqlite3.Connection, table: str, row_id: int, values: dict[str, object], pk_col: str = "id") -> int:
    cols = [k for k in values.keys() if k != pk_col]
    if not cols:
        return 0
    sets = ", ".join(f"{c}=?" for c in cols)
    params = [values[c] for c in cols] + [row_id]
    cur = conn.execute(f"UPDATE {table} SET {sets} WHERE {pk_col}=?", params)
    return cur.rowcount or 0


def delete_row(conn: sqlite3.Connection, table: str, row_id: int, pk_col: str = "id") -> int:
    cur = conn.execute(f"DELETE FROM {table} WHERE {pk_col}=?", (row_id,))
    return cur.rowcount or 0


def update_references_simple(conn: sqlite3.Connection, table: str, cols: Iterable[str], keep_id: int, dup_id: int) -> int:
    changed = 0
    for col in cols:
        cur = conn.execute(f"UPDATE {table} SET {col} = ? WHERE {col} = ?", (keep_id, dup_id))
        if cur.rowcount and cur.rowcount > 0:
            changed += cur.rowcount
    return changed


def main() -> int:
    p = argparse.ArgumentParser(description="Safe merge duplicate knowledge rows.")
    p.add_argument("--db", required=True, help="SQLite database path")
    p.add_argument("--backup-dir", default="backups", help="Backup directory")
    p.add_argument("--apply", action="store_true", help="Apply changes (default: dry-run)")
    p.add_argument("--auto-approve", action="store_true", help="Auto-approve conservative matches")
    p.add_argument("--approved-only", action="store_true", help="Only process rows with status='approved'")
    p.add_argument("--limit", type=int, default=0, help="Limit rows processed (0 = no limit)")
    args = p.parse_args()

    db_path = Path(args.db).expanduser().resolve()
    if not db_path.exists():
        raise SystemExit(f"Database not found: {db_path}")

    backup_path = backup_db(db_path, Path(args.backup_dir).expanduser().resolve())
    print(f"Backup created: {backup_path}")

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.execute("PRAGMA journal_mode=WAL;")

    knowledge_cols = table_columns(conn, "knowledge")
    content_col = detect_content_column(knowledge_cols)
    if "title" not in knowledge_cols or "category" not in knowledge_cols:
        raise SystemExit("knowledge table must contain title and category columns")
    if not content_col:
        raise SystemExit("Could not detect a content-like column in knowledge table")

    review_cols = table_columns(conn, "duplicate_review")
    if "status" not in review_cols:
        raise SystemExit("duplicate_review table must contain status column")

    fk_map = fk_targets(conn, "knowledge")
    unique_by_table = {table: unique_columns(conn, table) for table in fk_map.keys()}

    print("Tables with declared FK -> knowledge(id):")
    for t, cols in fk_map.items():
        extra = []
        for c in cols:
            if c in unique_by_table.get(t, set()):
                extra.append(f"{c} (unique)")
            else:
                extra.append(c)
        print(f"  {t}: {', '.join(extra)}")

    rows = conn.execute(
        f"""
        SELECT dr.keep_id, dr.duplicate_id, dr.score, dr.status,
               k1.title, k1.category, k1.{content_col},
               k2.title, k2.category, k2.{content_col}
        FROM duplicate_review dr
        JOIN knowledge k1 ON k1.id = dr.keep_id
        JOIN knowledge k2 ON k2.id = dr.duplicate_id
        {"WHERE dr.status='approved'" if args.approved_only else ""}
        ORDER BY dr.keep_id, dr.duplicate_id
        """
    ).fetchall()

    print(f"Review rows loaded: {len(rows)}")

    processed = 0
    merged = 0
    skipped = 0
    ref_updates_total = 0
    ref_merges_total = 0

    for row in rows:
        keep_id, dup_id, score, status, keep_title, keep_cat, keep_content, dup_title, dup_cat, dup_content = row

        safe = eligible_pair(keep_title, dup_title, keep_cat, dup_cat, keep_content, dup_content)
        if args.auto_approve and safe and status != "approved":
            if args.apply:
                conn.execute(
                    "UPDATE duplicate_review SET status='approved' WHERE keep_id=? AND duplicate_id=?",
                    (keep_id, dup_id),
                )
            status = "approved"

        if args.approved_only and status != "approved":
            skipped += 1
            continue

        if not safe and not args.approved_only:
            skipped += 1
            continue

        processed += 1
        merged_content = merge_text(keep_content, dup_content)
        content_changed = merged_content != (keep_content or "")

        if content_changed:
            print(f"[merge] keep={keep_id} dup={dup_id} title={keep_title}")
            print(f"  keep_len={len(keep_content or '')} dup_len={len(dup_content or '')} merged_len={len(merged_content)}")

        if args.apply:
            if content_changed:
                conn.execute(f"UPDATE knowledge SET {content_col}=? WHERE id=?", (merged_content, keep_id))

            for table, cols in fk_map.items():
                pk_cols = set(table_pk_columns(conn, table))
                pk_col_list = table_pk_columns(conn, table)
                pk_col = pk_col_list[0] if pk_col_list else "id"
                uniques = unique_by_table.get(table, set())

                for fk_col in cols:
                    if fk_col in uniques:
                        keep_row = row_by_fk(conn, table, fk_col, keep_id)
                        dup_row = row_by_fk(conn, table, fk_col, dup_id)

                        if keep_row and dup_row:
                            merged_row = merge_row_dicts(keep_row, dup_row, fk_col=fk_col, pk_cols=pk_cols)
                            keep_row_id = keep_row[pk_col]
                            merged_row[pk_col] = keep_row_id
                            update_row(conn, table, keep_row_id, merged_row, pk_col=pk_col)
                            delete_row(conn, table, dup_row[pk_col], pk_col=pk_col)
                            ref_merges_total += 1
                        elif not keep_row and dup_row:
                            conn.execute(
                                f"UPDATE {table} SET {fk_col}=? WHERE {pk_col}=?",
                                (keep_id, dup_row[pk_col]),
                            )
                            ref_updates_total += 1
                    else:
                        ref_updates_total += update_references_simple(conn, table, [fk_col], keep_id, dup_id)

            conn.execute("DELETE FROM knowledge WHERE id=?", (dup_id,))
            conn.execute(
                "UPDATE duplicate_review SET status='merged' WHERE keep_id=? AND duplicate_id=?",
                (keep_id, dup_id),
            )

        merged += 1
        if args.limit and processed >= args.limit:
            break

    if args.apply:
        conn.commit()
    else:
        conn.rollback()

    print("\nSummary")
    print(f"  processed:   {processed}")
    print(f"  merged:      {merged}")
    print(f"  skipped:     {skipped}")
    print(f"  ref updates: {ref_updates_total}")
    print(f"  ref merges:  {ref_merges_total}")
    print(f"  mode:        {'APPLY' if args.apply else 'DRY-RUN'}")

    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
