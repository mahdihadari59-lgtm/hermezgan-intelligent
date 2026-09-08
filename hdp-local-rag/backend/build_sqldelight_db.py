#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_sqldelight_db.py — ساخت hdp_database.db مطابق schema واقعی SQLDelight
                          (composeApp/src/commonMain/sqldelight/.../HdpDatabase.sq)

⚠️ منبع(ها) با mode=ro (فقط-خواندنی واقعی سطح SQLite) باز می‌شوند.
   خروجی همیشه یک فایل کاملاً جدید است؛ منابع هرگز تغییر نمی‌کنند.

نکته‌ی مهم: این نسخه جایگزین build_room_db.py قبلی است، چون معلوم شد
پروژه‌ی هدف نهایی (hdp-kotlin-app-complete) از Room استفاده نمی‌کند،
بلکه از SQLDelight با schema متفاوت (id عددی، cityId foreign key) استفاده می‌کند.

استفاده:
    python3 build_sqldelight_db.py \
        --source /data/data/com.termux/files/home/hormozgan_geo_project/hormozgan_data/hormozgan_geodata.db \
        --source2 /data/data/com.termux/files/home/hermezgan-intelligent/backend/hdp_import_v4/hdp_knowledge.db \
        --out hdp_database.db
"""

import argparse
import sqlite3
import sys
import time
from pathlib import Path

SCHEMA_SQL = """
CREATE TABLE CityEntity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    nameEn TEXT,
    province TEXT NOT NULL,
    population INTEGER DEFAULT 0,
    latitude REAL,
    longitude REAL,
    description TEXT,
    isActive INTEGER DEFAULT 1,
    createdAt INTEGER NOT NULL
);

CREATE TABLE AttractionEntity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    cityId INTEGER REFERENCES CityEntity(id),
    type TEXT NOT NULL,
    latitude REAL,
    longitude REAL,
    description TEXT,
    rating REAL DEFAULT 0.0,
    isActive INTEGER DEFAULT 1,
    createdAt INTEGER NOT NULL
);

CREATE TABLE BusinessEntity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    cityId INTEGER REFERENCES CityEntity(id),
    address TEXT,
    phone TEXT,
    latitude REAL,
    longitude REAL,
    rating REAL DEFAULT 0.0,
    isOpen INTEGER DEFAULT 1,
    isActive INTEGER DEFAULT 1,
    createdAt INTEGER NOT NULL
);

CREATE TABLE DialectWordEntity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT NOT NULL,
    dialect TEXT NOT NULL,
    meaning TEXT NOT NULL,
    standardPersian TEXT,
    example TEXT,
    pronunciation TEXT,
    isActive INTEGER DEFAULT 1
);

CREATE TABLE LegalDocEntity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    content TEXT NOT NULL,
    referenceNumber TEXT,
    issueDate INTEGER,
    isActive INTEGER DEFAULT 1
);

CREATE TABLE TrafficEntity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roadName TEXT NOT NULL,
    cityId INTEGER REFERENCES CityEntity(id),
    status TEXT NOT NULL,
    congestionLevel INTEGER DEFAULT 0,
    averageSpeed INTEGER DEFAULT 0,
    latitude REAL,
    longitude REAL,
    updatedAt INTEGER NOT NULL
);

CREATE TABLE RoadEntity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    cityId INTEGER REFERENCES CityEntity(id),
    startLat REAL,
    startLng REAL,
    endLat REAL,
    endLng REAL,
    lengthKm REAL,
    isActive INTEGER DEFAULT 1
);

CREATE TABLE VehicleFaultEntity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symptom TEXT NOT NULL,
    possibleCauses TEXT NOT NULL,
    severity TEXT NOT NULL,
    recommendedAction TEXT,
    estimatedCost TEXT
);

CREATE TABLE PoiEntity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    cityId INTEGER REFERENCES CityEntity(id),
    latitude REAL,
    longitude REAL,
    description TEXT,
    isActive INTEGER DEFAULT 1
);

CREATE INDEX idx_city_name ON CityEntity(name);
CREATE INDEX idx_attraction_city ON AttractionEntity(cityId);
CREATE INDEX idx_business_category ON BusinessEntity(category);
CREATE INDEX idx_dialect_word ON DialectWordEntity(word);
CREATE INDEX idx_traffic_road ON TrafficEntity(roadName);
CREATE INDEX idx_road_city ON RoadEntity(cityId);
"""


def col_exists(conn, table, col):
    try:
        cols = [r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()]
        return col in cols
    except sqlite3.OperationalError:
        return False


def table_exists(conn, table):
    return conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)
    ).fetchone() is not None


def lon_col(conn, table):
    for cand in ("lon", "lng", "longitude"):
        if col_exists(conn, table, cand):
            return cand
    return None


def now_ms():
    return int(time.time() * 1000)


def migrate_cities(src, dst):
    """منبع: cities در hormozgan_geodata.db (name_fa پر است، name خالی)."""
    if not table_exists(src, "cities"):
        return {}, 0
    name_col = "name_fa" if col_exists(src, "cities", "name_fa") else (
        "name" if col_exists(src, "cities", "name") else None
    )
    if not name_col:
        return {}, 0
    lon = lon_col(src, "cities")
    has_lat = col_exists(src, "cities", "lat")

    select_cols = f"{name_col}"
    select_cols += ", lat" if has_lat else ", NULL"
    select_cols += f", {lon}" if lon else ", NULL"
    select_cols += ", population" if col_exists(src, "cities", "population") else ", NULL"

    name_to_id = {}
    count = 0
    ts = now_ms()
    for row in src.execute(f"SELECT {select_cols} FROM cities WHERE {name_col} IS NOT NULL"):
        name, lat, lng, population = row
        if name is None or name in name_to_id:
            continue
        cur = dst.execute(
            "INSERT INTO CityEntity (name, nameEn, province, population, latitude, longitude, description, isActive, createdAt) "
            "VALUES (?, NULL, 'هرمزگان', ?, ?, ?, NULL, 1, ?)",
            (name, population or 0, lat, lng, ts),
        )
        name_to_id[name] = cur.lastrowid
        count += 1
    return name_to_id, count


def migrate_attractions(src, dst):
    count = 0
    ts = now_ms()
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
        for row in src.execute(f"SELECT {name_col}, lat, {lon} FROM {table}"):
            name, lat, lng = row
            if name is None or lat is None or lng is None:
                continue
            dst.execute(
                "INSERT INTO AttractionEntity (name, cityId, type, latitude, longitude, description, rating, isActive, createdAt) "
                "VALUES (?, NULL, ?, ?, ?, NULL, 0.0, 1, ?)",
                (name, category, lat, lng, ts),
            )
            count += 1
    return count


def migrate_businesses(src, dst):
    count = 0
    ts = now_ms()
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

        select_cols = f"{name_col}"
        select_cols += ", lat" if has_lat else ", NULL"
        select_cols += f", {lon}" if lon else ", NULL"
        select_cols += f", {phone_col}" if phone_col else ", NULL"
        select_cols += f", {addr_col}" if addr_col else ", NULL"

        for row in src.execute(f"SELECT {select_cols} FROM {table}"):
            name, lat, lng, phone, addr = row
            if name is None:
                continue
            dst.execute(
                "INSERT INTO BusinessEntity (name, category, cityId, address, phone, latitude, longitude, rating, isOpen, isActive, createdAt) "
                "VALUES (?, ?, NULL, ?, ?, ?, ?, 0.0, 1, 1, ?)",
                (name, category, addr, phone, lat, lng, ts),
            )
            count += 1
    return count


def migrate_pois(src, dst):
    count = 0
    ts = now_ms()
    sources = [
        ("pois", "poi"),
        ("fuel_stations", "fuel_station"),
        ("schools", "school"),
        ("hospitals", "hospital"),
    ]
    for table, ptype in sources:
        if not table_exists(src, table):
            continue
        lon = lon_col(src, table)
        if not lon or not col_exists(src, table, "lat"):
            continue
        name_col = "name" if col_exists(src, table, "name") else ("name_fa" if col_exists(src, table, "name_fa") else None)
        if not name_col:
            continue
        for row in src.execute(f"SELECT {name_col}, lat, {lon} FROM {table}"):
            name, lat, lng = row
            if name is None or lat is None or lng is None:
                continue
            dst.execute(
                "INSERT INTO PoiEntity (name, type, cityId, latitude, longitude, description, isActive) "
                "VALUES (?, ?, NULL, ?, ?, NULL, 1)",
                (name, ptype, lat, lng),
            )
            count += 1
    return count


def migrate_roads(src, dst, src2=None):
    """اولویت: routes در src2 (hdp_import_v4)، سقوط: traffic_data در src."""
    count = 0
    if src2 is not None and table_exists(src2, "routes"):
        for row in src2.execute(
            "SELECT origin, destination, distance, condition FROM routes WHERE origin IS NOT NULL"
        ):
            origin, destination, distance, condition = row
            name = f"{origin} → {destination}" if destination else origin
            dst.execute(
                "INSERT INTO RoadEntity (name, type, cityId, startLat, startLng, endLat, endLng, lengthKm, isActive) "
                "VALUES (?, 'route', NULL, NULL, NULL, NULL, NULL, ?, 1)",
                (name, distance),
            )
            count += 1
        if count > 0:
            return count

    if not table_exists(src, "traffic_data"):
        return 0
    lon = lon_col(src, "traffic_data")
    if not lon or not col_exists(src, "traffic_data", "road_name"):
        return 0
    for row in src.execute(f"SELECT road_name, lat, {lon} FROM traffic_data WHERE road_name IS NOT NULL"):
        name, lat, lng = row
        if name is None:
            continue
        dst.execute(
            "INSERT INTO RoadEntity (name, type, cityId, startLat, startLng, endLat, endLng, lengthKm, isActive) "
            "VALUES (?, 'urban', NULL, ?, ?, NULL, NULL, NULL, 1)",
            (name, lat, lng),
        )
        count += 1
    return count


def migrate_traffic(src, dst):
    """منبع: traffic_data (road_name, speed_kmh, congestion_level, lat/lon)."""
    if not table_exists(src, "traffic_data"):
        return 0
    lon = lon_col(src, "traffic_data")
    if not lon:
        return 0
    count = 0
    ts = now_ms()
    for row in src.execute(
        f"SELECT road_name, speed_kmh, congestion_level, lat, {lon} FROM traffic_data WHERE road_name IS NOT NULL"
    ):
        road_name, speed, congestion, lat, lng = row
        if road_name is None:
            continue
        status = congestion if congestion else "unknown"
        dst.execute(
            "INSERT INTO TrafficEntity (roadName, cityId, status, congestionLevel, averageSpeed, latitude, longitude, updatedAt) "
            "VALUES (?, NULL, ?, 0, ?, ?, ?, ?)",
            (road_name, status, int(speed) if speed else 0, lat, lng, ts),
        )
        count += 1
    return count


def main():
    parser = argparse.ArgumentParser(description="Build hdp_database.db matching the real SQLDelight schema (read-only sources)")
    parser.add_argument("--source", required=True, help="مسیر hormozgan_geodata.db (فقط خوانده می‌شود)")
    parser.add_argument("--source2", default=None, help="مسیر دوم اختیاری، hdp_import_v4/hdp_knowledge.db (فقط خوانده می‌شود)")
    parser.add_argument("--out", default="hdp_database.db", help="مسیر فایل خروجی جدید")
    args = parser.parse_args()

    source_path = Path(args.source).expanduser()
    out_path = Path(args.out).expanduser()

    if not source_path.exists():
        print(f"❌ دیتابیس مبدأ پیدا نشد: {source_path}")
        sys.exit(1)
    if out_path.exists():
        print(f"❌ فایل خروجی از قبل وجود دارد: {out_path} — برای جلوگیری از بازنویسی ناخواسته متوقف شد.")
        sys.exit(1)

    src2 = None
    if args.source2:
        source2_path = Path(args.source2).expanduser()
        if not source2_path.exists():
            print(f"❌ دیتابیس مبدأ دوم پیدا نشد: {source2_path}")
            sys.exit(1)
        src2 = sqlite3.connect(f"file:{source2_path}?mode=ro", uri=True)

    src = sqlite3.connect(f"file:{source_path}?mode=ro", uri=True)
    dst = sqlite3.connect(str(out_path))
    dst.executescript(SCHEMA_SQL)
    dst.commit()

    name_to_id, city_count = migrate_cities(src, dst)
    dst.commit()

    results = {
        "CityEntity": city_count,
        "AttractionEntity": migrate_attractions(src, dst),
        "BusinessEntity": migrate_businesses(src, dst),
        "PoiEntity": migrate_pois(src, dst),
        "RoadEntity": migrate_roads(src, dst, src2),
        "TrafficEntity": migrate_traffic(src, dst),
    }
    dst.commit()

    src.close()
    if src2 is not None:
        src2.close()
    dst.close()

    print("=" * 50)
    print(f"✅ hdp_database.db (schema واقعی SQLDelight) ساخته شد: {out_path}")
    for table, n in results.items():
        print(f"   {table}: {n} رکورد")
    print("=" * 50)
    print("⚠️ فعلاً cityId همه‌جا NULL است (نیاز به تطبیق جغرافیایی نزدیک‌ترین شهر — کار بعدی).")
    print("⚠️ DialectWordEntity, LegalDocEntity, VehicleFaultEntity هنوز پوشش داده نشده‌اند.")
    print("⚠️ AccidentHotspot در این schema اصلاً تعریف نشده (احتمالاً حذف/ادغام‌شده در TrafficEntity).")


if __name__ == "__main__":
    main()
