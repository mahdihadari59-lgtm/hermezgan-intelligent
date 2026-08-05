#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HDP Atlas importer for SQLite.

Targets:
- neighborhoods
- traffic_cameras
- traffic_blackspots
- fuel_stations

Optional:
- rebuild FTS5 tables if they exist
- print before/after counts

Usage:
  python3 hdp_import_atlas.py /path/to/hdp_v2.db

Notes:
- The script introspects table schemas and only inserts columns that exist.
- It skips duplicate rows when a stable name/title already exists.
- It does not assume a fixed schema beyond SQLite table names.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


DB_PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("hdp_v2.db")

# ---------------------------------------------------------------------
# Source data extracted from the atlas that was shared in chat.
# ---------------------------------------------------------------------

NEIGHBORHOODS = [
    # Region 1
    {"name": "سورو", "region": "۱", "region_name": "مرکز و شمال غرب", "type": "قدیمی", "usage": "مسکونی-تجاری", "lat": 27.170615, "lon": 56.242385},
    {"name": "سید کامل", "region": "۱", "region_name": "مرکز و شمال غرب", "type": "قدیمی", "usage": "مسکونی", "lat": 27.165637, "lon": 56.239251},
    {"name": "نایبند", "region": "۱", "region_name": "مرکز و شمال غرب", "type": "قدیمی", "usage": "مسکونی-تجاری", "lat": 27.173123, "lon": 56.242848},
    {"name": "برکه گرد", "region": "۱", "region_name": "مرکز و شمال غرب", "type": "قدیمی", "usage": "مسکونی", "lat": 27.177306, "lon": 56.255243},
    {"name": "پشت شهر", "region": "۱", "region_name": "مرکز و شمال غرب", "type": "قدیمی", "usage": "مسکونی", "lat": 27.178152, "lon": 56.271648},
    {"name": "سه راه برق", "region": "۱", "region_name": "مرکز و شمال غرب", "type": "تجاری", "usage": "اداری-تجاری", "lat": 27.182096, "lon": 56.273599},
    # Region 2
    {"name": "گلشهر", "region": "۲", "region_name": "شمال و شمال شرق", "type": "جدید", "usage": "مسکونی-تجاری", "lat": 27.204462, "lon": 56.342583},
    {"name": "بهشت بندر", "region": "۲", "region_name": "شمال و شمال شرق", "type": "جدید", "usage": "مسکونی", "lat": 27.199675, "lon": 56.350212},
    {"name": "داماهی", "region": "۲", "region_name": "شمال و شمال شرق", "type": "جدید", "usage": "مسکونی", "lat": 27.209913, "lon": 56.353214},
    {"name": "آزادگان", "region": "۲", "region_name": "شمال و شمال شرق", "type": "جدید", "usage": "مسکونی", "lat": 27.205664, "lon": 56.348989},
    {"name": "زیباشهر", "region": "۲", "region_name": "شمال و شمال شرق", "type": "جدید", "usage": "مسکونی", "lat": 27.209712, "lon": 56.335948},
    # Region 3
    {"name": "نخل ناخدا", "region": "۳", "region_name": "شرق و جنوب شرق", "type": "قدیمی-جدید", "usage": "مسکونی-تجاری", "lat": 27.198376, "lon": 56.350634},
    {"name": "خواجه عطاء", "region": "۳", "region_name": "شرق و جنوب شرق", "type": "قدیمی", "usage": "مسکونی", "lat": 27.184265, "lon": 56.302658},
    {"name": "کوی ۲۲ بهمن", "region": "۳", "region_name": "شرق و جنوب شرق", "type": "جدید", "usage": "مسکونی", "lat": 27.194863, "lon": 56.305142},
    {"name": "شمیلی‌ها", "region": "۳", "region_name": "شرق و جنوب شرق", "type": "قدیمی", "usage": "مسکونی", "lat": 27.188960, "lon": 56.319210},
    {"name": "سرریگ", "region": "۳", "region_name": "شرق و جنوب شرق", "type": "قدیمی", "usage": "مسکونی", "lat": 27.185274, "lon": 56.310505},
    # Region 4
    {"name": "سیم بالا", "region": "۴", "region_name": "جنوب و جنوب غرب (ساحلی)", "type": "جدید", "usage": "مسکونی", "lat": 27.175075, "lon": 56.267913},
    {"name": "شغو (شهرک توحید)", "region": "۴", "region_name": "جنوب و جنوب غرب (ساحلی)", "type": "جدید", "usage": "مسکونی", "lat": 27.172960, "lon": 56.261303},
    {"name": "اوزی‌ها", "region": "۴", "region_name": "جنوب و جنوب غرب (ساحلی)", "type": "قدیمی", "usage": "مسکونی-تجاری", "lat": 27.178301, "lon": 56.277264},
    {"name": "ششصد دستگاه", "region": "۴", "region_name": "جنوب و جنوب غرب (ساحلی)", "type": "جدید", "usage": "مسکونی", "lat": 27.179328, "lon": 56.283722},
    {"name": "امیرآباد", "region": "۴", "region_name": "جنوب و جنوب غرب (ساحلی)", "type": "جدید", "usage": "مسکونی", "lat": 27.194120, "lon": 56.283450},
    {"name": "چهارصد دستگاه", "region": "۴", "region_name": "جنوب و جنوب غرب (ساحلی)", "type": "جدید", "usage": "مسکونی", "lat": 27.190000, "lon": 56.290500},
    # Region 5
    {"name": "دوهزار", "region": "۵", "region_name": "غرب (ورودی شهر)", "type": "جدید", "usage": "مسکونی", "lat": 27.187575, "lon": 56.245915},
    {"name": "شهید جعفری", "region": "۵", "region_name": "غرب (ورودی شهر)", "type": "جدید", "usage": "مسکونی", "lat": 27.190812, "lon": 56.248479},
    {"name": "کوی ولیعصر", "region": "۵", "region_name": "غرب (ورودی شهر)", "type": "جدید", "usage": "مسکونی", "lat": 27.195160, "lon": 56.244950},
]

TRAFFIC_CAMERAS = [
    # Active
    {"name": "چهارراه غزی", "lat": 27.185497, "lon": 56.283742, "camera_type": "چراغ قرمز+سرعت", "status": "فعال", "priority": "بالا"},
    {"name": "میدان سپاه", "lat": 27.190000, "lon": 56.295000, "camera_type": "چراغ قرمز", "status": "فعال", "priority": "متوسط"},
    {"name": "بلوار امام خمینی (بیمارستان محمدی)", "lat": 27.194820, "lon": 56.296853, "camera_type": "سرعت", "status": "فعال", "priority": "بالا"},
    {"name": "سه راه برق", "lat": 27.182096, "lon": 56.273599, "camera_type": "چراغ قرمز", "status": "فعال", "priority": "بالا"},
    {"name": "بلوار شهید رجایی", "lat": 27.195000, "lon": 56.350000, "camera_type": "سرعت+پلاک‌خوان", "status": "فعال", "priority": "بالا"},
    {"name": "میدان ولیعصر", "lat": 27.200800, "lon": 56.300900, "camera_type": "نظارتی+چراغ قرمز", "status": "فعال", "priority": "متوسط"},
    {"name": "چهارراه قدس", "lat": 27.188995, "lon": 56.276623, "camera_type": "چراغ قرمز", "status": "فعال", "priority": "بالا"},
    {"name": "چهارراه جهانبار", "lat": 27.185000, "lon": 56.296500, "camera_type": "چراغ قرمز", "status": "فعال", "priority": "بالا"},
    {"name": "میدان انقلاب", "lat": 27.182500, "lon": 56.256000, "camera_type": "سرعت", "status": "فعال", "priority": "متوسط"},
    {"name": "میدان امام خمینی", "lat": 27.185700, "lon": 56.289900, "camera_type": "چراغ قرمز", "status": "فعال", "priority": "بالا"},
    {"name": "پل شهدا", "lat": 27.210000, "lon": 56.344000, "camera_type": "سرعت+پلاک‌خوان", "status": "فعال", "priority": "بالا"},
    {"name": "خیابان آیت‌الله غفاری", "lat": 27.188000, "lon": 56.282000, "camera_type": "سرعت", "status": "فعال", "priority": "متوسط"},
    {"name": "بلوار خلیج فارس", "lat": 27.180000, "lon": 56.260000, "camera_type": "سرعت", "status": "در حال نصب", "priority": "بالا"},
    {"name": "بلوار سرباز (ساحل سورو)", "lat": 27.170100, "lon": 56.247860, "camera_type": "سرعت+پلاک‌خوان", "status": "در حال نصب", "priority": "بالا"},
    # Proposed / recommended
    {"name": "تقاطع پاسداران-هرمز", "lat": 27.178000, "lon": 56.268000, "camera_type": "چراغ قرمز+سرعت", "status": "پیشنهادی", "priority": "فوری"},
    {"name": "چهارراه سازمان", "lat": 27.190000, "lon": 56.305000, "camera_type": "چراغ قرمز", "status": "پیشنهادی", "priority": "فوری"},
    {"name": "بلوار طالقانی", "lat": 27.183500, "lon": 56.280000, "camera_type": "سرعت", "status": "پیشنهادی", "priority": "بالا"},
    {"name": "بلوار دانشگاه", "lat": 27.194574, "lon": 56.265506, "camera_type": "سرعت", "status": "پیشنهادی", "priority": "بالا"},
    {"name": "خیابان شریعتی", "lat": 27.184000, "lon": 56.292000, "camera_type": "چراغ قرمز", "status": "پیشنهادی", "priority": "متوسط"},
]

TRAFFIC_BLACKSPOTS = [
    {"name": "بلوار مصطفی خمینی (ساحل سورو)", "lat": 27.175600, "lon": 56.267700, "severity": "بسیار بالا", "reason": "دوردور، تجمع خودروها، برخورد با عابر", "suggestion": "نصب دوربین سرعت + پلاک‌خوان، افزایش گشت پلیس، نورپردازی بهتر"},
    {"name": "چهارراه غزی", "lat": 27.185497, "lon": 56.283742, "severity": "بالا", "reason": "تزریق خودرو از خیابان‌های فرعی، عدم توجه به چراغ قرمز", "suggestion": "دوربین چراغ قرمز + سرعت، اصلاح هندسی تقاطع"},
    {"name": "جاده بندر شهید رجایی", "lat": 27.195000, "lon": 56.450000, "severity": "بالا", "reason": "سرعت بالا، سبقت غیرمجاز، تردد ناوگان سنگین", "suggestion": "رادار سرعت + پلاک‌خوان، تابلوهای هشدار، جداسازی مسیر ناوگان سنگین"},
    {"name": "بلوار خلیج فارس", "lat": 27.180000, "lon": 56.260000, "severity": "متوسط", "reason": "سرعت بالا در شب، نبود دوربین کافی", "suggestion": "دوربین سرعت + IR شب، تابلوهای محدودیت سرعت"},
    {"name": "میدان ولیعصر", "lat": 27.200800, "lon": 56.300900, "severity": "متوسط", "reason": "رفتار دوردور، عدم رعایت حق تقدم", "suggestion": "دوربین نظارتی، اصلاح مسیر ورودی و خروجی"},
]

FUEL_STATIONS = [
    {"name": "پمپ بنزین و گاز جرون", "lat": 27.241184, "lon": 56.360980, "fuel_type": "بنزین-گازوئیل-CNG"},
    {"name": "پمپ بنزین ایسین", "lat": 27.289025, "lon": 56.269134, "fuel_type": "بنزین-گازوئیل"},
    {"name": "جایگاه CNG", "lat": 27.220472, "lon": 56.257946, "fuel_type": "CNG"},
    {"name": "پمپ بنزین دریای جنوب", "lat": 27.188602, "lon": 56.289677, "fuel_type": "بنزین-گازوئیل"},
    {"name": "پمپ بنزین سادات", "lat": 27.196587, "lon": 56.260109, "fuel_type": "بنزین"},
    {"name": "پمپ گاز و بنزین پامرو", "lat": 27.209476, "lon": 56.314907, "fuel_type": "بنزین-CNG"},
    {"name": "جایگاه بنزین سامکو", "lat": 27.221715, "lon": 56.337211, "fuel_type": "بنزین"},
    {"name": "پمپ بنزین بلال", "lat": 27.205465, "lon": 56.348939, "fuel_type": "بنزین"},
    {"name": "پمپ بنزین ناصر", "lat": 27.167850, "lon": 56.242463, "fuel_type": "بنزین"},
    {"name": "جایگاه شهید عوض پور", "lat": 27.188697, "lon": 56.307266, "fuel_type": "بنزین-CNG"},
    {"name": "پمپ بنزین خلیج فارس", "lat": 27.210034, "lon": 56.313181, "fuel_type": "بنزین-گازوئیل"},
]

# Optional: seed the knowledge/places tables with normalized atlas rows.
# These are broader than the four target tables and are inserted only if
# the table schema contains compatible columns.
ATLAS_KNOWLEDGE_DOCS = [
    {
        "title": "اطلس ترافیک و مسیریابی هوشمند بندرعباس",
        "category": "atlas",
        "subcategory": "traffic",
        "content": "نسخه 2.0 پیشرفته از اطلس ترافیک و مسیریابی بندرعباس، شامل محلات، دوربین‌ها، جایگاه‌های سوخت، مراکز درمانی، آموزشی، پارکینگ‌ها، مسیرهای اصلی و نقاط حادثه‌خیز.",
        "priority": 5,
        "city": "بندرعباس",
    },
    {
        "title": "جایگاه‌های سوخت بندرعباس",
        "category": "atlas",
        "subcategory": "fuel",
        "content": "فهرست جایگاه‌های سوخت و CNG بندرعباس با مختصات واقعی و نوع سوخت.",
        "priority": 4,
        "city": "بندرعباس",
    },
    {
        "title": "دوربین‌های هوشمند بندرعباس",
        "category": "atlas",
        "subcategory": "traffic",
        "content": "فهرست دوربین‌های فعال، در حال نصب و پیشنهادی بندرعباس با نوع دوربین و وضعیت.",
        "priority": 4,
        "city": "بندرعباس",
    },
    {
        "title": "نقاط حادثه‌خیز بندرعباس",
        "category": "atlas",
        "subcategory": "traffic",
        "content": "نقاط پرخطر با اولویت‌بندی و پیشنهادهای ایمن‌سازی.",
        "priority": 4,
        "city": "بندرعباس",
    },
]

# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

SYNONYMS: Dict[str, Tuple[str, ...]] = {
    "name": ("name", "title", "place_name", "station_name"),
    "title": ("title", "name"),
    "lat": ("lat", "latitude", "y"),
    "lon": ("lon", "lng", "long", "longitude", "x"),
    "region": ("region", "zone"),
    "region_name": ("region_name", "district_name", "area_name"),
    "type": ("type", "kind", "category", "camera_type", "fuel_type", "usage"),
    "camera_type": ("camera_type", "type", "category"),
    "status": ("status", "state"),
    "priority": ("priority", "rank"),
    "city": ("city",),
    "usage": ("usage", "use", "usage_type"),
    "severity": ("severity", "level"),
    "reason": ("reason", "cause", "description"),
    "suggestion": ("suggestion", "proposal", "recommendation"),
    "fuel_type": ("fuel_type", "type", "category"),
    "subcategory": ("subcategory",),
    "category": ("category",),
    "content": ("content", "description", "note"),
}

def table_exists(conn: sqlite3.Connection, table: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (table,),
    ).fetchone()
    return row is not None

def fts_exists(conn: sqlite3.Connection, table: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE name=? AND sql LIKE '%fts5%'",
        (table,),
    ).fetchone()
    return row is not None

def get_columns(conn: sqlite3.Connection, table: str) -> List[str]:
    try:
        return [r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()]
    except sqlite3.Error:
        return []

def get_table_sql(conn: sqlite3.Connection, table: str) -> str:
    row = conn.execute("SELECT sql FROM sqlite_master WHERE name=?", (table,)).fetchone()
    return row[0] if row and row[0] else ""

def pick_value(record: Dict[str, Any], col: str) -> Any:
    candidates = SYNONYMS.get(col, (col,))
    for key in candidates:
        if key in record and record[key] is not None:
            return record[key]
    return None

def normalize_row(record: Dict[str, Any], columns: Sequence[str]) -> Dict[str, Any]:
    row: Dict[str, Any] = {}
    for col in columns:
        if col in ("id", "rowid"):
            continue
        value = pick_value(record, col)
        if value is not None:
            row[col] = value
    return row

def existing_names(conn: sqlite3.Connection, table: str, columns: Sequence[str]) -> set:
    name_col = None
    for candidate in ("name", "title"):
        if candidate in columns:
            name_col = candidate
            break
    if not name_col:
        return set()
    try:
        return {r[0] for r in conn.execute(f"SELECT {name_col} FROM {table}").fetchall() if r[0] is not None}
    except sqlite3.Error:
        return set()

def insert_records(conn: sqlite3.Connection, table: str, records: Sequence[Dict[str, Any]], dedupe_key_candidates: Sequence[str] = ("name", "title")) -> int:
    if not table_exists(conn, table):
        print(f"⚠️  table missing: {table}")
        return 0

    cols = get_columns(conn, table)
    if not cols:
        print(f"⚠️  no columns found for: {table}")
        return 0

    insertable_cols = [c for c in cols if c not in ("id", "rowid")]
    if not insertable_cols:
        print(f"⚠️  no insertable columns for: {table}")
        return 0

    # Determine a practical dedupe key.
    dedupe_col = None
    for candidate in dedupe_key_candidates:
        if candidate in cols:
            dedupe_col = candidate
            break

    existing = set()
    if dedupe_col:
        try:
            existing = {r[0] for r in conn.execute(f"SELECT {dedupe_col} FROM {table}").fetchall() if r[0] is not None}
        except sqlite3.Error:
            existing = set()

    inserted = 0
    for record in records:
        row = normalize_row(record, insertable_cols)

        if dedupe_col:
            dval = row.get(dedupe_col)
            if dval is None and dedupe_col in ("name", "title"):
                dval = record.get("name") or record.get("title")
            if dval is not None and dval in existing:
                continue
            if dval is not None:
                existing.add(dval)

        if not row:
            continue

        columns = list(row.keys())
        placeholders = ", ".join(["?"] * len(columns))
        col_sql = ", ".join(columns)
        values = [row[c] for c in columns]
        try:
            conn.execute(
                f"INSERT INTO {table} ({col_sql}) VALUES ({placeholders})",
                values,
            )
            inserted += 1
        except sqlite3.IntegrityError:
            # Skip duplicate/constraint failure
            continue
        except sqlite3.Error as exc:
            print(f"⚠️  insert failed in {table}: {exc}")
            continue

    conn.commit()
    return inserted

def rebuild_fts(conn: sqlite3.Connection) -> List[str]:
    rebuilt = []
    for (name, sql) in conn.execute(
        "SELECT name, sql FROM sqlite_master WHERE type='table' AND sql LIKE '%fts5%'"
    ).fetchall():
        try:
            conn.execute(f"INSERT INTO {name}({name}) VALUES('rebuild')")
            rebuilt.append(name)
        except sqlite3.Error:
            # Some FTS tables may not support rebuild in a given config.
            pass
    conn.commit()
    return rebuilt

def count_rows(conn: sqlite3.Connection, table: str) -> Optional[int]:
    if not table_exists(conn, table):
        return None
    try:
        return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    except sqlite3.Error:
        return None

def print_counts(conn: sqlite3.Connection, tables: Sequence[str], label: str) -> None:
    print(f"\n=== {label} ===")
    for t in tables:
        n = count_rows(conn, t)
        if n is None:
            print(f"{t:20s} : missing")
        else:
            print(f"{t:20s} : {n}")

def maybe_seed_knowledge(conn: sqlite3.Connection) -> int:
    if not table_exists(conn, "knowledge"):
        return 0
    cols = get_columns(conn, "knowledge")
    if not cols:
        return 0

    # Seed only if table has compatible columns.
    seed_docs = []
    for doc in ATLAS_KNOWLEDGE_DOCS:
        row = normalize_row(doc, cols)
        if row:
            seed_docs.append(row)

    inserted = 0
    existing = set()
    for key in ("title", "name"):
        if key in cols:
            try:
                existing = {r[0] for r in conn.execute(f"SELECT {key} FROM knowledge").fetchall() if r[0] is not None}
            except sqlite3.Error:
                existing = set()
            break

    for row in seed_docs:
        dedupe = row.get("title") or row.get("name")
        if dedupe and dedupe in existing:
            continue
        columns = list(row.keys())
        try:
            conn.execute(
                f"INSERT INTO knowledge ({', '.join(columns)}) VALUES ({', '.join(['?'] * len(columns))})",
                [row[c] for c in columns],
            )
            inserted += 1
            if dedupe:
                existing.add(dedupe)
        except sqlite3.Error:
            continue

    conn.commit()
    return inserted

def main() -> int:
    if not DB_PATH.exists():
        print(f"❌ database not found: {DB_PATH}")
        return 1

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row

    target_tables = [
        "knowledge",
        "knowledge_fts",
        "unified_search",
        "places",
        "hospitals",
        "fuel_stations",
        "traffic_cameras",
        "traffic_blackspots",
        "neighborhoods",
    ]

    print_counts(conn, target_tables, "before")

    # Seed a few normalized docs into knowledge if the schema allows it.
    seeded_knowledge = maybe_seed_knowledge(conn)
    if seeded_knowledge:
        print(f"✅ seeded knowledge docs: {seeded_knowledge}")

    inserted = {}
    inserted["neighborhoods"] = insert_records(conn, "neighborhoods", NEIGHBORHOODS)
    inserted["traffic_cameras"] = insert_records(conn, "traffic_cameras", TRAFFIC_CAMERAS)
    inserted["traffic_blackspots"] = insert_records(conn, "traffic_blackspots", TRAFFIC_BLACKSPOTS)
    inserted["fuel_stations"] = insert_records(conn, "fuel_stations", FUEL_STATIONS)

    for table, n in inserted.items():
        print(f"✅ inserted into {table}: {n}")

    rebuilt = rebuild_fts(conn)
    if rebuilt:
        print("✅ rebuilt FTS tables:", ", ".join(rebuilt))
    else:
        print("ℹ️  no FTS tables rebuilt (or rebuild skipped by schema)")

    conn.execute("ANALYZE")
    conn.commit()

    print_counts(conn, target_tables, "after")
    conn.close()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
