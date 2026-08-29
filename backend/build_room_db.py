#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_room_db.py — ساخت دیتابیس سازگار با Room (اپ اندروید RAG-HDP)
                    از روی hormozgan_geodata.db

⚠️ منبع (hormozgan_geodata.db) با حالت mode=ro (فقط-خواندنی واقعی سطح
   SQLite) باز می‌شود — هیچ نوشتنی روی آن ممکن نیست، حتی در صورت باگ.
   خروجی همیشه یک فایل کاملاً جدید و جداست؛ فایل مبدأ هرگز تغییر نمی‌کند.

schema مقصد دقیقاً از روی این Entity های Kotlin واقعی گرفته شده:
  PoiEntity, BusinessEntity, RoadEntity, CityEntity,
  AttractionEntity, AccidentHotspotEntity

استفاده:
    python3 build_room_db.py \
        --source /data/data/com.termux/files/home/hormozgan_geo_project/hormozgan_data/hormozgan_geodata.db \
        --out hdp_room_knowledge.db
"""

import argparse
import sqlite3
import sys
from pathlib import Path

# ------------------------------------------------------------------
# تعریف دقیق جدول‌های مقصد — منطبق با @Entity های Kotlin
# ------------------------------------------------------------------
ROOM_SCHEMA = {
    "pois": """
        CREATE TABLE pois (
            id TEXT PRIMARY KEY NOT NULL,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            subCategory TEXT,
            address TEXT,
            lat REAL NOT NULL,
            lng REAL NOT NULL,
            phone TEXT,
            rating REAL,
            openingHours TEXT,
            description TEXT,
            isVerified INTEGER NOT NULL DEFAULT 0
        )
    """,
    "businesses": """
        CREATE TABLE businesses (
            id TEXT PRIMARY KEY NOT NULL,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            subCategory TEXT,
            address TEXT,
            lat REAL,
            lng REAL,
            phone TEXT,
            rating REAL,
            workingHours TEXT,
            services TEXT,
            isOpen INTEGER NOT NULL DEFAULT 1,
            lastVerified INTEGER NOT NULL DEFAULT 0
        )
    """,
    "roads": """
        CREATE TABLE roads (
            id TEXT PRIMARY KEY NOT NULL,
            name TEXT NOT NULL,
            nameEn TEXT,
            type TEXT NOT NULL,
            fromCity TEXT NOT NULL,
            toCity TEXT,
            distanceKm REAL,
            condition TEXT NOT NULL,
            restrictions TEXT,
            coordinates TEXT
        )
    """,
    "cities": """
        CREATE TABLE cities (
            id TEXT PRIMARY KEY NOT NULL,
            name TEXT NOT NULL,
            nameEn TEXT,
            province TEXT NOT NULL,
            population TEXT,
            area TEXT,
            description TEXT,
            neighborhoods TEXT,
            landmarks TEXT,
            lat REAL,
            lng REAL
        )
    """,
    "attractions": """
        CREATE TABLE attractions (
            id TEXT PRIMARY KEY NOT NULL,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            lat REAL NOT NULL,
            lng REAL NOT NULL,
            rating REAL,
            bestTimeToVisit TEXT,
            entryFee TEXT,
            openingHours TEXT,
            images TEXT
        )
    """,
    "accident_hotspots": """
        CREATE TABLE accident_hotspots (
            id TEXT PRIMARY KEY NOT NULL,
            location TEXT NOT NULL,
            lat REAL NOT NULL,
            lng REAL NOT NULL,
            accidentCount INTEGER NOT NULL,
            severity TEXT NOT NULL,
            mainCause TEXT,
            recommendations TEXT
        )
    """,
}


def col_exists(conn, table, col):
    try:
        cols = [r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()]
        return col in cols
    except sqlite3.OperationalError:
        return False


def table_exists(conn, table):
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)
    ).fetchone()
    return row is not None


def lon_col(conn, table):
    """اسم واقعی ستون طول جغرافیایی را در جدول مبدأ پیدا می‌کند (lon یا lng)."""
    for cand in ("lon", "lng", "longitude"):
        if col_exists(conn, table, cand):
            return cand
    return None


def severity_to_text(value) -> str:
    """severity عددی (۱-۵) منبع را به رشته‌ی low/medium/high موردنیاز Room تبدیل می‌کند."""
    try:
        v = int(value)
    except (TypeError, ValueError):
        return "medium"
    if v <= 2:
        return "low"
    if v <= 3:
        return "medium"
    return "high"


def migrate_pois(src, dst):
    """منبع: pois + fuel_stations + schools + hospitals (به‌عنوان انواع POI)."""
    count = 0
    sources = [
        ("pois", "pois", None),
        ("fuel_stations", "fuel_station", None),
        ("schools", "school", "name_fa"),
        ("hospitals", "hospital", None),
    ]
    for table, category, name_col_override in sources:
        if not table_exists(src, table):
            continue
        lon = lon_col(src, table)
        if not lon or not col_exists(src, table, "lat"):
            continue
        name_col = name_col_override or ("name" if col_exists(src, table, "name") else None)
        if not name_col:
            continue
        phone_col = "phone" if col_exists(src, table, "phone") else None
        addr_col = "address" if col_exists(src, table, "address") else None

        select_cols = f"rowid, {name_col}, lat, {lon}"
        select_cols += f", {phone_col}" if phone_col else ", NULL"
        select_cols += f", {addr_col}" if addr_col else ", NULL"

        for row in src.execute(f"SELECT {select_cols} FROM {table}"):
            rowid, name, lat, lng, phone, addr = row
            if lat is None or lng is None or name is None:
                continue
            uid = f"{table}_{rowid}"
            dst.execute(
                "INSERT OR IGNORE INTO pois (id, name, category, subCategory, address, lat, lng, phone, rating, openingHours, description, isVerified) "
                "VALUES (?, ?, ?, NULL, ?, ?, ?, ?, NULL, NULL, NULL, 0)",
                (uid, name, category, addr, lat, lng, phone),
            )
            count += 1
    return count


def migrate_businesses(src, dst):
    """منبع: cafes + restaurants + hotels + shopping_centers."""
    count = 0
    sources = [
        ("cafes", "cafe"),
        ("restaurants", "restaurant"),
        ("hotels", "hotel"),
        ("shopping_centers", "shopping"),
    ]
    for table, category in sources:
        if not table_exists(src, table):
            continue
        lon = lon_col(src, table)
        has_lat = col_exists(src, table, "lat")
        name_col = "name" if col_exists(src, table, "name") else ("name_fa" if col_exists(src, table, "name_fa") else None)
        if not name_col:
            continue
        phone_col = "phone" if col_exists(src, table, "phone") else None
        addr_col = "address" if col_exists(src, table, "address") else None

        select_cols = f"rowid, {name_col}"
        select_cols += f", lat" if has_lat else ", NULL"
        select_cols += f", {lon}" if lon else ", NULL"
        select_cols += f", {phone_col}" if phone_col else ", NULL"
        select_cols += f", {addr_col}" if addr_col else ", NULL"

        for row in src.execute(f"SELECT {select_cols} FROM {table}"):
            rowid, name, lat, lng, phone, addr = row
            if name is None:
                continue
            uid = f"{table}_{rowid}"
            dst.execute(
                "INSERT OR IGNORE INTO businesses (id, name, category, subCategory, address, lat, lng, phone, rating, workingHours, services, isOpen, lastVerified) "
                "VALUES (?, ?, ?, NULL, ?, ?, ?, ?, NULL, NULL, NULL, 1, 0)",
                (uid, name, category, addr, lat, lng, phone),
            )
            count += 1
    return count


def migrate_roads(src, dst):
    if not table_exists(src, "roads"):
        return 0
    count = 0
    name_col = "name" if col_exists(src, "roads", "name") else None
    if not name_col:
        return 0
    for row in src.execute(f"SELECT rowid, {name_col} FROM roads"):
        rowid, name = row
        if name is None:
            continue
        uid = f"road_{rowid}"
        dst.execute(
            "INSERT OR IGNORE INTO roads (id, name, nameEn, type, fromCity, toCity, distanceKm, condition, restrictions, coordinates) "
            "VALUES (?, ?, NULL, 'unknown', 'بندرعباس', NULL, NULL, 'unknown', NULL, NULL)",
            (uid, name),
        )
        count += 1
    return count


def migrate_cities(src, dst):
    if not table_exists(src, "city_info"):
        return 0
    count = 0
    for row in src.execute("SELECT rowid, * FROM city_info"):
        cols = [d[0] for d in src.execute("SELECT * FROM city_info LIMIT 1").description]
        break
    # ساده‌سازی: فقط اگر ستون name موجود باشد
    if not col_exists(src, "city_info", "name") and not col_exists(src, "city_info", "name_fa"):
        return 0
    name_col = "name" if col_exists(src, "city_info", "name") else "name_fa"
    lon = lon_col(src, "city_info")
    has_lat = col_exists(src, "city_info", "lat")

    select_cols = f"rowid, {name_col}"
    select_cols += ", lat" if has_lat else ", NULL"
    select_cols += f", {lon}" if lon else ", NULL"

    for row in src.execute(f"SELECT {select_cols} FROM city_info"):
        rowid, name, lat, lng = row
        if name is None:
            continue
        uid = f"city_{rowid}"
        dst.execute(
            "INSERT OR IGNORE INTO cities (id, name, nameEn, province, population, area, description, neighborhoods, landmarks, lat, lng) "
            "VALUES (?, ?, NULL, 'هرمزگان', NULL, NULL, NULL, NULL, NULL, ?, ?)",
            (uid, name, lat, lng),
        )
        count += 1
    return count


def migrate_attractions(src, dst):
    count = 0
    sources = [
        ("tourist_areas", "cultural"),
        ("natural_attractions", "natural"),
        ("cultural_sites", "cultural"),
        ("religious_sites", "cultural"),
    ]
    for table, category in sources:
        if not table_exists(src, table):
            continue
        lon = lon_col(src, table)
        if not lon or not col_exists(src, table, "lat"):
            continue
        name_col = "name" if col_exists(src, table, "name") else ("name_fa" if col_exists(src, table, "name_fa") else None)
        if not name_col:
            continue
        for row in src.execute(f"SELECT rowid, {name_col}, lat, {lon} FROM {table}"):
            rowid, name, lat, lng = row
            if name is None or lat is None or lng is None:
                continue
            uid = f"{table}_{rowid}"
            dst.execute(
                "INSERT OR IGNORE INTO attractions (id, name, category, description, lat, lng, rating, bestTimeToVisit, entryFee, openingHours, images) "
                "VALUES (?, ?, ?, NULL, ?, ?, NULL, NULL, NULL, NULL, NULL)",
                (uid, name, category, lat, lng),
            )
            count += 1
    return count


def migrate_accident_hotspots(src, dst):
    if not table_exists(src, "hotspots_info"):
        return 0
    lon = lon_col(src, "hotspots_info")
    if not lon or not col_exists(src, "hotspots_info", "lat"):
        # خیلی از نسخه‌های قبلی hotspots_info اصلاً lat/lon نداشتند — در آن صورت رد می‌شویم
        return 0
    count = 0
    for row in src.execute(
        f"SELECT rowid, name, lat, {lon}, accidents, severity FROM hotspots_info"
    ):
        rowid, name, lat, lng, accidents, severity = row
        if name is None or lat is None or lng is None:
            continue
        uid = f"hotspot_{rowid}"
        dst.execute(
            "INSERT OR IGNORE INTO accident_hotspots (id, location, lat, lng, accidentCount, severity, mainCause, recommendations) "
            "VALUES (?, ?, ?, ?, ?, ?, NULL, NULL)",
            (uid, name, lat, lng, accidents or 0, severity_to_text(severity)),
        )
        count += 1
    return count


def main():
    parser = argparse.ArgumentParser(description="Build a Room-compatible SQLite db for RAG-HDP Android app (read-only source)")
    parser.add_argument("--source", required=True, help="مسیر hormozgan_geodata.db (فقط خوانده می‌شود)")
    parser.add_argument("--out", default="hdp_room_knowledge.db", help="مسیر فایل خروجی جدید")
    args = parser.parse_args()

    source_path = Path(args.source).expanduser()
    out_path = Path(args.out).expanduser()

    if not source_path.exists():
        print(f"❌ دیتابیس مبدأ پیدا نشد: {source_path}")
        sys.exit(1)

    if out_path.exists():
        print(f"❌ فایل خروجی از قبل وجود دارد: {out_path} — برای جلوگیری از بازنویسی ناخواسته متوقف شد. اسم دیگری بده یا حذفش کن.")
        sys.exit(1)

    # اتصال کاملاً فقط-خواندنی به منبع — تضمین‌شده در سطح SQLite
    src = sqlite3.connect(f"file:{source_path}?mode=ro", uri=True)

    # مقصد: فایل کاملاً جدید
    dst = sqlite3.connect(str(out_path))
    for table, ddl in ROOM_SCHEMA.items():
        dst.execute(ddl)
    dst.commit()

    results = {
        "pois": migrate_pois(src, dst),
        "businesses": migrate_businesses(src, dst),
        "roads": migrate_roads(src, dst),
        "cities": migrate_cities(src, dst),
        "attractions": migrate_attractions(src, dst),
        "accident_hotspots": migrate_accident_hotspots(src, dst),
    }
    dst.commit()

    src.close()
    dst.close()

    print("=" * 50)
    print(f"✅ دیتابیس Room ساخته شد: {out_path}")
    for table, n in results.items():
        print(f"   {table}: {n} رکورد")
    print("=" * 50)
    print("⚠️ فقط ۶ جدول (pois, businesses, roads, cities, attractions, accident_hotspots) پوشش داده شد.")
    print("   جدول‌های دیگر Room (legal, dialect, traffic, vehicle_fault) هنوز نیاز به schema دقیق دارند.")


if __name__ == "__main__":
    main()
