#!/usr/bin/env python3
# ============================================================
# db_audit.py - بررسی کامل ساختار دیتابیس و جداول
# ============================================================
"""
استفاده:
    python3 db_audit.py مسیر/به/دیتابیس.db
    python3 db_audit.py hormozgan_geodata.db --sample 3
"""
import sqlite3
import sys
import os
import argparse


def human_size(num_bytes):
    for unit in ["B", "KB", "MB", "GB"]:
        if num_bytes < 1024:
            return f"{num_bytes:.1f}{unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f}TB"


def main():
    parser = argparse.ArgumentParser(description="بررسی کامل دیتابیس SQLite")
    parser.add_argument("db_path", help="مسیر فایل دیتابیس")
    parser.add_argument("--sample", type=int, default=0,
                         help="تعداد رکورد نمونه برای نمایش از هر جدول (پیش‌فرض 0)")
    args = parser.parse_args()

    if not os.path.exists(args.db_path):
        print(f"❌ فایل پیدا نشد: {args.db_path}")
        sys.exit(1)

    file_size = os.path.getsize(args.db_path)
    print("=" * 70)
    print(f"📦 دیتابیس: {args.db_path}")
    print(f"💾 حجم فایل: {human_size(file_size)}")
    print("=" * 70)

    conn = sqlite3.connect(args.db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # --- لیست جداول ---
    cur.execute("""
        SELECT name, sql FROM sqlite_master
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """)
    tables = cur.fetchall()

    if not tables:
        print("⚠️ هیچ جدولی پیدا نشد.")
        return

    print(f"\n📋 تعداد جداول: {len(tables)}\n")

    table_stats = []
    for t in tables:
        name = t["name"]
        try:
            cur.execute(f"SELECT COUNT(*) as c FROM [{name}]")
            count = cur.fetchone()["c"]
        except sqlite3.Error as e:
            count = f"خطا: {e}"
        table_stats.append((name, count))

    # مرتب‌سازی بر اساس تعداد رکورد (نزولی)
    def sort_key(item):
        return item[1] if isinstance(item[1], int) else -1

    table_stats.sort(key=sort_key, reverse=True)

    print(f"{'جدول':<35}{'تعداد رکورد':>15}")
    print("-" * 50)
    for name, count in table_stats:
        count_str = f"{count:,}" if isinstance(count, int) else str(count)
        marker = " ⚠️ خالی" if count == 0 else ""
        print(f"{name:<35}{count_str:>15}{marker}")

    # --- هشدار جداول با اسم مشابه (احتمال duplicate schema) ---
    print("\n" + "=" * 70)
    print("🔎 بررسی جداول با نام مشابه (احتمال duplicate/parallel schema)")
    print("=" * 70)
    names = [t[0] for t in table_stats]
    grouped = {}
    for n in names:
        base = n.rstrip("0123456789").rstrip("_v").rstrip("_")
        # ساده‌سازی: حذف پسوندهای رایج نسخه‌بندی
        for suffix in ["_backup", "_old", "_before_cleanup", "_v2", "_v3", "_new", "_bak"]:
            if base.endswith(suffix):
                base = base[: -len(suffix)]
        grouped.setdefault(base, []).append(n)

    suspicious = {k: v for k, v in grouped.items() if len(v) > 1}
    if suspicious:
        for base, variants in suspicious.items():
            print(f"\n  گروه '{base}':")
            for v in variants:
                cnt = dict(table_stats)[v]
                print(f"     - {v} ({cnt if isinstance(cnt, int) else cnt} رکورد)")
    else:
        print("\n  ✅ جدول مشابه/مشکوکی پیدا نشد.")

    # --- ستون‌های هر جدول ---
    print("\n" + "=" * 70)
    print("🧩 ساختار ستون‌ها")
    print("=" * 70)
    for name, count in table_stats:
        cur.execute(f"PRAGMA table_info([{name}])")
        cols = cur.fetchall()
        col_desc = ", ".join(f"{c['name']}:{c['type']}" for c in cols)
        print(f"\n▸ {name} ({len(cols)} ستون)")
        print(f"   {col_desc}")

        if args.sample > 0 and isinstance(count, int) and count > 0:
            try:
                cur.execute(f"SELECT * FROM [{name}] LIMIT {args.sample}")
                rows = cur.fetchall()
                for r in rows:
                    row_dict = dict(r)
                    preview = {k: (str(v)[:40] + "…" if v and len(str(v)) > 40 else v)
                               for k, v in row_dict.items()}
                    print(f"   نمونه: {preview}")
            except sqlite3.Error as e:
                print(f"   (خطا در خواندن نمونه: {e})")

    # --- ایندکس‌ها ---
    print("\n" + "=" * 70)
    print("📑 ایندکس‌ها")
    print("=" * 70)
    cur.execute("""
        SELECT name, tbl_name, sql FROM sqlite_master
        WHERE type='index' AND sql IS NOT NULL
        ORDER BY tbl_name
    """)
    indexes = cur.fetchall()
    if indexes:
        for idx in indexes:
            print(f"  {idx['tbl_name']:<30} ← {idx['name']}")
    else:
        print("  ⚠️ هیچ ایندکس دستی‌ای پیدا نشد (فقط ایندکس‌های خودکار sqlite).")

    # --- توابع/تریگرها/ویوها ---
    cur.execute("SELECT name, type FROM sqlite_master WHERE type IN ('view','trigger') ORDER BY type, name")
    others = cur.fetchall()
    if others:
        print("\n" + "=" * 70)
        print("👁️  ویوها و تریگرها")
        print("=" * 70)
        for o in others:
            print(f"  [{o['type']}] {o['name']}")

    conn.close()
    print("\n✅ بررسی کامل شد.")


if __name__ == "__main__":
    main()
