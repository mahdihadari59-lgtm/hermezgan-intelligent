#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Full audit of hdp_v2.db: schema, columns, row counts, text/content stats,
and duplicate detection across every table that looks like it holds
title+content style knowledge rows.

Read-only. Never writes to the database. Writes a full report to a text
file (report is long) and prints a shorter summary to the terminal.

Usage:
  python3 audit_db.py --db backend/hdp_v2.db
  python3 audit_db.py --db backend/hdp_v2.db --out audit_report.txt
"""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path


TEXT_CANDIDATES = (
    "content", "body", "text", "description", "summary",
    "answer", "detail", "details", "notes", "value_text", "value",
)


def table_list(conn: sqlite3.Connection) -> list[str]:
    return [
        r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name NOT LIKE 'sqlite_%' ORDER BY name"
        ).fetchall()
    ]


def table_info(conn: sqlite3.Connection, table: str) -> list[tuple]:
    return conn.execute(f"PRAGMA table_info({table})").fetchall()


def table_schema_sql(conn: sqlite3.Connection, table: str) -> str:
    row = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table,)
    ).fetchone()
    return row[0] if row else ""


def row_count(conn: sqlite3.Connection, table: str) -> int:
    return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


def detect_content_col(cols: list[str]) -> str | None:
    for c in TEXT_CANDIDATES:
        if c in cols:
            return c
    return None


def main() -> int:
    p = argparse.ArgumentParser(description="Full DB audit")
    p.add_argument("--db", required=True)
    p.add_argument("--out", default="audit_report.txt")
    p.add_argument("--sample", type=int, default=3, help="Sample rows to show per table")
    args = p.parse_args()

    db_path = Path(args.db).expanduser().resolve()
    if not db_path.exists():
        raise SystemExit(f"Database not found: {db_path}")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    out_lines: list[str] = []

    def w(line: str = "") -> None:
        out_lines.append(line)

    w("=" * 70)
    w(f"DATABASE AUDIT REPORT — {db_path}")
    w("=" * 70)

    tables = table_list(conn)
    w(f"\nTotal tables: {len(tables)}\n")

    # ---- overview table ----
    w("-" * 70)
    w("TABLE OVERVIEW")
    w("-" * 70)
    overview = []
    for t in tables:
        try:
            n = row_count(conn, t)
        except Exception as e:
            n = -1
        cols = [c[1] for c in table_info(conn, t)]
        overview.append((t, n, len(cols)))
        w(f"  {t:<30} rows={n:<8} cols={len(cols)}")

    # ---- per-table detail ----
    w("\n" + "-" * 70)
    w("PER-TABLE SCHEMA + COLUMN DETAIL")
    w("-" * 70)
    for t in tables:
        w(f"\n### {t}")
        w(table_schema_sql(conn, t))
        w("  columns:")
        for c in table_info(conn, t):
            cid, name, ctype, notnull, dflt, pk = c
            flags = []
            if pk:
                flags.append("PK")
            if notnull:
                flags.append("NOT NULL")
            if dflt is not None:
                flags.append(f"DEFAULT {dflt}")
            flag_str = f" [{', '.join(flags)}]" if flags else ""
            w(f"    - {name} ({ctype}){flag_str}")

    # ---- content-bearing tables: text stats ----
    w("\n" + "-" * 70)
    w("TEXTUAL CONTENT STATS (tables with a detected content column)")
    w("-" * 70)
    for t in tables:
        cols = [c[1] for c in table_info(conn, t)]
        content_col = detect_content_col(cols)
        if not content_col:
            continue
        n = row_count(conn, t)
        if n == 0:
            continue
        lens = conn.execute(
            f"SELECT LENGTH({content_col}) FROM {t} WHERE {content_col} IS NOT NULL"
        ).fetchall()
        lens = [r[0] for r in lens]
        null_count = n - len(lens)
        empty_count = conn.execute(
            f"SELECT COUNT(*) FROM {t} WHERE {content_col} IS NULL OR TRIM({content_col})=''"
        ).fetchone()[0]
        w(f"\n### {t}.{content_col}")
        w(f"  rows: {n}")
        w(f"  null: {null_count}   empty/blank: {empty_count}")
        if lens:
            w(f"  length min/avg/max: {min(lens)} / {sum(lens)//len(lens)} / {max(lens)}")

        # duplicate title+category (if such columns exist)
        if "title" in cols:
            cat_expr = "IFNULL(category,'')" if "category" in cols else "''"
            dup_row = conn.execute(
                f"SELECT COUNT(*) - COUNT(DISTINCT title||'|'||{cat_expr}) FROM {t}"
            ).fetchone()[0]
            w(f"  duplicate (title+category) rows: {dup_row}")

    # ---- global duplicate breakdown for `knowledge` by category ----
    if "knowledge" in tables:
        cols = [c[1] for c in table_info(conn, "knowledge")]
        if "title" in cols and "category" in cols:
            w("\n" + "-" * 70)
            w("KNOWLEDGE TABLE — DUPLICATES BY CATEGORY")
            w("-" * 70)
            rows = conn.execute(
                """
                SELECT category, COUNT(*) as dup_rows FROM (
                    SELECT category, title
                    FROM knowledge
                    GROUP BY title, category
                    HAVING COUNT(*) > 1
                )
                GROUP BY category
                ORDER BY dup_rows DESC
                """
            ).fetchall()
            for r in rows:
                w(f"  {r['category']:<15} {r['dup_rows']} duplicate title groups")

            w("\nKNOWLEDGE TABLE — CATEGORY BREAKDOWN")
            rows = conn.execute(
                "SELECT category, COUNT(*) as n FROM knowledge GROUP BY category ORDER BY n DESC"
            ).fetchall()
            for r in rows:
                w(f"  {r['category']:<15} {r['n']}")

    # ---- sample rows per table ----
    if args.sample > 0:
        w("\n" + "-" * 70)
        w(f"SAMPLE ROWS (first {args.sample} per table)")
        w("-" * 70)
        for t in tables:
            n = row_count(conn, t)
            if n == 0:
                continue
            w(f"\n### {t} (showing {min(args.sample, n)} of {n})")
            rows = conn.execute(f"SELECT * FROM {t} LIMIT {args.sample}").fetchall()
            for r in rows:
                d = dict(r)
                parts = []
                for k, v in d.items():
                    sv = str(v) if v is not None else "NULL"
                    if len(sv) > 80:
                        sv = sv[:80] + "…"
                    parts.append(f"{k}={sv}")
                w("  " + " | ".join(parts))

    conn.close()

    report = "\n".join(out_lines)
    out_path = Path(args.out)
    out_path.write_text(report, encoding="utf-8")

    # terminal summary (short)
    print(f"Full report written to: {out_path.resolve()}  ({len(out_lines)} lines)")
    print()
    print("=" * 50)
    print("QUICK SUMMARY")
    print("=" * 50)
    for t, n, ncols in overview:
        print(f"  {t:<30} rows={n:<8} cols={ncols}")
    print()
    print(f"View the full report with:\n  less {out_path}\nor open it as a file.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
