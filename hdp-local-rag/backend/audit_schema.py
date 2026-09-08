#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
audit_schema.py — گزارش‌گیری فقط-خواندنی از ناهماهنگی نام ستون‌ها در کل دیتابیس

⚠️ این اسکریپت هیچ تغییری در دیتابیس ایجاد نمی‌کند — فقط SELECT/PRAGMA می‌زند.
کاملاً امن است که مستقیم روی hormozgan_master_final.db اجرا شود.

خروجی: یک گزارش Markdown که برای هر «مفهوم» (مثل طول جغرافیایی) نشان می‌دهد
کدام جدول‌ها از کدام نام ستون استفاده می‌کنند، و کدام نام باید به‌عنوان
نام استاندارد (canonical) انتخاب شود.

استفاده:
    python3 audit_schema.py --db /path/to/hormozgan_master_final.db --out schema_audit_report.md
"""

import argparse
import sqlite3
from collections import defaultdict
from pathlib import Path

# ------------------------------------------------------------------
# گروه‌های مفهومی: هر مفهوم چند نام رایج ممکن دارد.
# این لیست را می‌توان بر اساس نتیجه‌ی اجرا گسترش داد.
# ------------------------------------------------------------------
CONCEPT_GROUPS = {
    "latitude": ["lat", "latitude"],
    "longitude": ["lon", "lng", "longitude", "long"],
    "name": ["name", "name_fa", "title", "label"],
    "name_en": ["name_en", "name_english", "title_en"],
    "phone": ["phone", "tel", "telephone", "phone_number"],
    "address": ["address", "location", "addr"],
    "category": ["category", "type", "cat"],
    "description": ["description", "desc", "definition", "details"],
    "created_at": ["created_at", "collected_at", "timestamp", "date_added"],
    "city": ["city", "city_name", "shahr"],
    "district": ["district", "neighborhood", "zone", "mahalleh"],
    "source": ["source", "source_reference", "data_source"],
    "confidence": ["confidence", "confidence_score", "score"],
    "id_ref": ["poi_id", "related_poi_id", "entity_id"],
}


def get_all_tables(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    ).fetchall()
    return [r[0] for r in rows]


def get_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    try:
        return [r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()]
    except sqlite3.Error:
        return []


def build_report(conn: sqlite3.Connection) -> str:
    tables = get_all_tables(conn)
    table_columns = {t: get_columns(conn, t) for t in tables}

    lines = []
    lines.append("# 📋 گزارش ناهماهنگی نام ستون‌ها\n")
    lines.append(f"تعداد کل جدول‌ها: **{len(tables)}**\n")

    # --------------------------------------------------------------
    # بخش ۱: برای هر مفهوم، کدام جدول‌ها کدام نام را استفاده می‌کنند
    # --------------------------------------------------------------
    lines.append("## بخش ۱ — ناهماهنگی به تفکیک مفهوم\n")

    concept_geo_incomplete = []  # جدول‌هایی که فقط lat یا فقط lon دارن، نه هردو

    for concept, candidates in CONCEPT_GROUPS.items():
        name_to_tables = defaultdict(list)
        for table, cols in table_columns.items():
            for cand in candidates:
                if cand in cols:
                    name_to_tables[cand].append(table)

        used_names = list(name_to_tables.keys())
        if len(used_names) == 0:
            continue

        # نام غالب = نامی که بیشترین جدول از آن استفاده می‌کند
        canonical = max(name_to_tables, key=lambda n: len(name_to_tables[n]))
        total_tables_with_concept = sum(len(v) for v in name_to_tables.values())

        lines.append(f"### مفهوم: `{concept}`")
        if len(used_names) > 1:
            lines.append(f"⚠️ **ناهماهنگ** — {len(used_names)} نام مختلف برای این مفهوم استفاده شده:\n")
        else:
            lines.append("✅ همگی از یک نام استفاده می‌کنند:\n")

        for name in sorted(used_names, key=lambda n: -len(name_to_tables[n])):
            marker = " ← 🏆 پیشنهاد به‌عنوان نام استاندارد" if name == canonical and len(used_names) > 1 else ""
            table_list = name_to_tables[name]
            lines.append(f"- `{name}` در **{len(table_list)}** جدول{marker}")
            if len(table_list) <= 15:
                lines.append(f"  - {', '.join(table_list)}")
            else:
                lines.append(f"  - {', '.join(table_list[:15])}, ... و {len(table_list) - 15} جدول دیگر")
        lines.append("")

    # --------------------------------------------------------------
    # بخش ۲: جدول‌هایی که مختصات ناقص دارند (فقط lat یا فقط lon)
    # --------------------------------------------------------------
    lines.append("## بخش ۲ — جدول‌هایی با مختصات ناقص (فقط lat یا فقط lon/lng)\n")
    lat_names = CONCEPT_GROUPS["latitude"]
    lon_names = CONCEPT_GROUPS["longitude"]
    for table, cols in table_columns.items():
        has_lat = any(c in cols for c in lat_names)
        has_lon = any(c in cols for c in lon_names)
        if has_lat != has_lon:
            missing = "longitude" if has_lat else "latitude"
            lines.append(f"- ⚠️ `{table}` — دارای {'lat' if has_lat else 'lon/lng'} اما بدون {missing}")
    lines.append("")

    # --------------------------------------------------------------
    # بخش ۳: جدول‌هایی با نام‌های ستونی که در هیچ گروه مفهومی جا نمی‌شوند
    # (فقط برای آگاهی — لزوماً مشکل نیست)
    # --------------------------------------------------------------
    all_known = {c for candidates in CONCEPT_GROUPS.values() for c in candidates}
    lines.append("## بخش ۳ — جدول‌ها و تعداد ستون‌های ناشناخته (خارج از گروه‌های تعریف‌شده بالا)\n")
    lines.append("این بخش صرفاً اطلاعاتی است — یعنی ستون‌هایی که مخصوص همان جدول‌اند (طبیعی است).\n")
    for table, cols in sorted(table_columns.items(), key=lambda kv: -len(kv[1])):
        unknown = [c for c in cols if c not in all_known and c not in ("id", "created_at")]
        if unknown:
            lines.append(f"- `{table}` ({len(cols)} ستون کل): {', '.join(unknown[:10])}"
                          + (f", ... +{len(unknown) - 10}" if len(unknown) > 10 else ""))

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Read-only schema naming audit")
    parser.add_argument("--db", required=True, help="مسیر دیتابیس (فقط خوانده می‌شود، هیچ نوشتنی انجام نمی‌شود)")
    parser.add_argument("--out", default="schema_audit_report.md", help="مسیر فایل خروجی گزارش")
    args = parser.parse_args()

    db_path = Path(args.db).expanduser()
    if not db_path.exists():
        print(f"❌ دیتابیس پیدا نشد: {db_path}")
        return

    # اتصال فقط-خواندنی (immutable) — تضمین می‌کند حتی به‌اشتباه هم چیزی نوشته نمی‌شود
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)

    report = build_report(conn)
    conn.close()

    out_path = Path(args.out)
    out_path.write_text(report, encoding="utf-8")
    print(f"✅ گزارش ساخته شد: {out_path}")
    print(f"   ({len(report.splitlines())} خط)")


if __name__ == "__main__":
    main()
