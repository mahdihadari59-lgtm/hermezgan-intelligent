#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
merge_to_master.py — انتقال داده‌ی خام از یک دیتابیس مبدأ به hormozgan_master_final.db
با تشخیص خودکار ستون‌های مشترک و جلوگیری از ورود رکورد تکراری (dedup).

نحوه‌ی استفاده:
    python3 merge_to_master.py --source /path/to/source.db --target /path/to/hormozgan_master_final.db --tables pois,fuel_stations,schools

    یا برای merge کل جدول‌های مشترک بین دو دیتابیس:
    python3 merge_to_master.py --source /path/to/source.db --target /path/to/hormozgan_master_final.db --all-common

قبل از اجرا، خودکار از فایل مقصد بکاپ می‌گیرد (کنار فایل اصلی، با پسوند .pre_merge_<timestamp>.bak).

منطق dedup برای هر جدول:
  1) اگر در TABLE_DEDUP_KEYS یک کلید طبیعی تعریف شده باشد (مثلاً name+lat+lon)، از همان استفاده می‌شود.
  2) در غیر این صورت، یک هش SHA-256 از تمام مقادیر ستون‌های مشترک (به‌جز id/pk) ساخته و به‌عنوان کلید یکتایی مقایسه می‌شود.

هر خطای سطح-ردیف (type mismatch، NOT NULL و غیره) لاگ می‌شود و کل عملیات را متوقف نمی‌کند.
"""

import argparse
import hashlib
import logging
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("merge")

# ------------------------------------------------------------------
# کلیدهای طبیعی برای dedup دقیق‌تر (اختیاری). هر جدولی که اینجا نباشد
# با هش کل محتوای ردیف (fallback) مقایسه می‌شود.
# فقط ستون‌هایی که واقعاً در هر دو جدول مبدأ/مقصد موجودند اعمال می‌شوند.
# ------------------------------------------------------------------
TABLE_DEDUP_KEYS = {
    "pois": ["name", "lat", "lon"],
    "fuel_stations": ["name", "lat", "lon"],
    "cafes": ["name", "lat", "lon"],
    "restaurants": ["name", "lat", "lon"],
    "hotels": ["name", "lat", "lon"],
    "schools": ["name_fa", "lat", "lon"],
    "private_schools": ["name", "lat", "lon"],
    "hospitals": ["name", "lat", "lon"],
    "parks": ["name_fa", "lat", "lon"],
    "roads": ["name", "lat", "lon"],
    "hotspots_info": ["name", "severity", "accidents", "fatalities"],
    "traffic_data": ["road_name", "lat", "lon", "timestamp"],
    "bandari_vocabulary": ["word_standard", "word_bandari"],
    "bandari_phrases": ["phrase_bandari"],
    "bandari_proverbs": ["proverb_bandari"],
    "bandari_dialogues": ["text_bandari"],
    "graph_nodes": ["id"],
    "graph_relations": ["source_entity_id", "target_entity_id", "relation_type_id"],
}

# ------------------------------------------------------------------
# مترادف‌های شناخته‌شده‌ی ستون‌ها. وقتی نام ستون مقصد مستقیم در مبدأ
# پیدا نشد، این لیست‌ها برای پیدا کردن معادل بررسی می‌شوند.
# این جلوی موردی مثل «مقصد: lon، مبدأ: lng» را می‌گیرد که قبلاً
# باعث می‌شد lon بی‌صدا NULL بماند بدون هیچ خطایی.
# ------------------------------------------------------------------
COLUMN_ALIASES = {
    "lon": ["lng", "longitude", "long"],
    "lng": ["lon", "longitude", "long"],
    "lat": ["latitude"],
    "name": ["name_fa", "title", "label"],
    "name_fa": ["name", "title", "label"],
    "phone": ["phone_number", "tel", "telephone"],
    "address": ["location", "addr"],
}


def backup_target(target_path: Path) -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = target_path.with_suffix(f".pre_merge_{ts}.bak")
    shutil.copy2(target_path, backup_path)

    # تأیید صحت بکاپ: اندازه باید دقیقاً برابر باشه
    original_size = target_path.stat().st_size
    backup_size = backup_path.stat().st_size
    if backup_size != original_size:
        raise RuntimeError(
            f"❌ بکاپ ناقص است! اصلی: {original_size} بایت، بکاپ: {backup_size} بایت. عملیات متوقف شد."
        )

    # تأیید صحت با باز کردن بکاپ و شمارش جدول‌ها
    try:
        test_conn = sqlite3.connect(str(backup_path))
        table_count = test_conn.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table'"
        ).fetchone()[0]
        test_conn.close()
        if table_count == 0:
            raise RuntimeError("❌ بکاپ خالی است یا قابل خواندن نیست. عملیات متوقف شد.")
    except sqlite3.Error as e:
        raise RuntimeError(f"❌ بکاپ سالم نیست، قابل باز شدن با sqlite3 نبود: {e}")

    log.info(f"✅ بکاپ ساخته و تأیید شد ({table_count} جدول، {backup_size} بایت): {backup_path}")
    return backup_path


def get_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    cur = conn.execute(f"PRAGMA table_info({table})")
    return [row[1] for row in cur.fetchall()]


def get_pk_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    cur = conn.execute(f"PRAGMA table_info({table})")
    return [row[1] for row in cur.fetchall() if row[5] > 0]


def common_tables(src: sqlite3.Connection, dst: sqlite3.Connection) -> list[str]:
    src_tables = {
        r[0] for r in src.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
    }
    dst_tables = {
        r[0] for r in dst.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
    }
    return sorted(src_tables & dst_tables)


def row_hash(values: tuple) -> str:
    normalized = "|".join("" if v is None else str(v).strip() for v in values)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def build_existing_key_set(dst: sqlite3.Connection, table: str, key_cols: list[str], use_hash: bool):
    """کلیدهای موجود در جدول مقصد را برای مقایسه‌ی سریع در حافظه می‌سازد."""
    cols_sql = ", ".join(key_cols)
    existing = set()
    try:
        for row in dst.execute(f"SELECT {cols_sql} FROM {table}"):
            existing.add(row_hash(row) if use_hash else row)
    except sqlite3.OperationalError as e:
        log.warning(f"  ⚠️ نتونستم کلیدهای موجود {table} رو بخونم: {e}")
    return existing


def resolve_column_pairs(src_cols: list[str], dst_cols: list[str], dst_pk: set[str]) -> list[tuple[str, str]]:
    """
    برای هر ستون مقصد (به‌جز PK)، معادلش را در مبدأ پیدا می‌کند:
    اول تطبیق دقیق نام، بعد بررسی مترادف‌های شناخته‌شده در COLUMN_ALIASES.
    خروجی: لیست (dst_col, src_col) — فقط ستون‌هایی که معادل پیدا شد.
    """
    pairs = []
    src_cols_set = set(src_cols)
    for dst_col in dst_cols:
        if dst_col in dst_pk:
            continue
        if dst_col in src_cols_set:
            pairs.append((dst_col, dst_col))
            continue
        for alias in COLUMN_ALIASES.get(dst_col, []):
            if alias in src_cols_set:
                pairs.append((dst_col, alias))
                break
    return pairs


def merge_table(src: sqlite3.Connection, dst: sqlite3.Connection, table: str) -> dict:
    src_cols = get_columns(src, table)
    dst_cols = get_columns(dst, table)
    dst_pk = set(get_pk_columns(dst, table))

    col_pairs = resolve_column_pairs(src_cols, dst_cols, dst_pk)
    if not col_pairs:
        return {"table": table, "inserted": 0, "skipped": 0, "errors": 0, "note": "no matching columns (even with aliases)"}

    # گزارش شفاف نگاشت‌ها — به‌خصوص مواردی که از طریق alias (نه تطبیق مستقیم) پیدا شدند
    aliased = [f"{s}→{d}" for d, s in col_pairs if s != d]
    if aliased:
        log.info(f"    🔗 نگاشت مترادف اعمال شد: {', '.join(aliased)}")

    dst_names = [d for d, s in col_pairs]
    src_names = [s for d, s in col_pairs]

    dedup_key = TABLE_DEDUP_KEYS.get(table)
    if dedup_key:
        key_cols = [c for c in dedup_key if c in dst_names]
        use_hash = len(key_cols) == 0
        if use_hash:
            key_cols = dst_names
    else:
        key_cols = dst_names
        use_hash = True

    existing_keys = build_existing_key_set(dst, table, key_cols, use_hash)

    select_sql = f"SELECT {', '.join(src_names)} FROM {table}"
    insert_sql = f"INSERT INTO {table} ({', '.join(dst_names)}) VALUES ({', '.join(['?'] * len(dst_names))})"
    key_idx = [dst_names.index(c) for c in key_cols]

    inserted = skipped = errors = 0

    try:
        src_rows = src.execute(select_sql).fetchall()
    except sqlite3.OperationalError as e:
        return {"table": table, "inserted": 0, "skipped": 0, "errors": 1, "note": f"select failed: {e}"}

    for row in src_rows:
        key_values = tuple(row[i] for i in key_idx)
        key = row_hash(key_values) if use_hash else key_values

        if key in existing_keys:
            skipped += 1
            continue

        try:
            dst.execute(insert_sql, row)
            existing_keys.add(key)
            inserted += 1
        except sqlite3.Error as e:
            errors += 1
            log.debug(f"  ردیف رد شد در {table}: {e}")

    return {"table": table, "inserted": inserted, "skipped": skipped, "errors": errors, "note": ""}


def main():
    parser = argparse.ArgumentParser(description="Merge raw data into hormozgan_master_final.db with dedup")
    parser.add_argument("--source", required=True, help="مسیر دیتابیس مبدأ (داده‌ی خام)")
    parser.add_argument("--target", required=True, help="مسیر hormozgan_master_final.db")
    parser.add_argument("--tables", help="لیست جدول‌ها با کاما جدا شده (پیش‌فرض: خالی)")
    parser.add_argument("--all-common", action="store_true", help="merge تمام جدول‌های مشترک بین مبدأ و مقصد")
    parser.add_argument("--no-backup", action="store_true", help="از بکاپ خودکار صرف‌نظر کن (به‌شدت توصیه نمی‌شود)")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="بدون این پرچم، اسکریپت فقط dry-run است (هیچ چیزی روی دیسک نوشته نمی‌شود). "
             "فقط وقتی خروجی dry-run را بررسی و تأیید کردی این پرچم را اضافه کن.",
    )
    parser.add_argument(
        "--target-copy-test",
        help="به‌جای دست‌زدن به target اصلی، یک کپی کامل در این مسیر می‌سازد و merge را فقط روی آن کپی اجرا می‌کند "
             "(حتی با --execute). برای تست کامل بدون هیچ ریسکی روی داده‌ی عملیاتی.",
    )
    args = parser.parse_args()

    source_path = Path(args.source).expanduser()
    target_path = Path(args.target).expanduser()

    if not source_path.exists():
        log.error(f"❌ دیتابیس مبدأ پیدا نشد: {source_path}")
        sys.exit(1)
    if not target_path.exists():
        log.error(f"❌ دیتابیس مقصد پیدا نشد: {target_path}")
        sys.exit(1)

    dry_run = not args.execute

    # حالت امن‌ترین: merge روی یک کپی کاملاً جدا، بدون هیچ تماسی با فایل اصلی
    if args.target_copy_test:
        test_target = Path(args.target_copy_test).expanduser()
        shutil.copy2(target_path, test_target)
        log.info(f"🧪 حالت تست ایزوله: merge فقط روی کپی {test_target} اجرا می‌شود. فایل اصلی دست‌نخورده می‌ماند.")
        target_path = test_target
        dry_run = False  # چون داریم روی کپی کار می‌کنیم، نوشتن روی این کپی بی‌خطره
    elif dry_run:
        log.warning("🔍 حالت DRY-RUN: هیچ تغییری روی دیتابیس مقصد ذخیره نخواهد شد (فقط شبیه‌سازی و گزارش).")
        log.warning("   برای اجرای واقعی، بعد از بررسی نتیجه، پرچم --execute را اضافه کن.")

    if not args.no_backup and not args.target_copy_test:
        backup_target(target_path)

    src = sqlite3.connect(str(source_path))
    dst = sqlite3.connect(str(target_path))

    if args.all_common:
        tables = common_tables(src, dst)
        log.info(f"📋 {len(tables)} جدول مشترک پیدا شد: {', '.join(tables)}")
    elif args.tables:
        tables = [t.strip() for t in args.tables.split(",") if t.strip()]
    else:
        log.error("❌ باید --tables یا --all-common بدی")
        sys.exit(1)

    results = []
    try:
        for table in tables:
            log.info(f"▶ در حال merge: {table}")
            result = merge_table(src, dst, table)
            results.append(result)
            note = f" ({result['note']})" if result["note"] else ""
            log.info(
                f"  ✅ {'(dry-run) ' if dry_run else ''}insert می‌شد/شد: {result['inserted']} "
                f"| ⏭️ تکراری رد شد: {result['skipped']} | ❌ خطا: {result['errors']}{note}"
            )

        if dry_run:
            dst.rollback()
            log.info("🔍 DRY-RUN تمام شد — هیچ تغییری ذخیره نشد.")
        else:
            dst.commit()
            log.info("💾 تغییرات commit شد.")
    except Exception as e:
        dst.rollback()
        log.error(f"❌ خطای بحرانی رخ داد، همه‌چیز rollback شد: {e}")
        raise
    finally:
        src.close()
        dst.close()

    total_inserted = sum(r["inserted"] for r in results)
    total_skipped = sum(r["skipped"] for r in results)
    total_errors = sum(r["errors"] for r in results)

    log.info("=" * 60)
    log.info(f"📊 خلاصه‌ی نهایی: {total_inserted} ردیف جدید | {total_skipped} تکراری رد شد | {total_errors} خطا")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
