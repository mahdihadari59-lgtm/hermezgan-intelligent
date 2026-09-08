#!/usr/bin/env python3
"""
seed_data.py — populate geo.db with sample Hormozgan data for dev/testing.

Mirrors the fallback arrays already in the frontend layers (CameraLayer.jsx,
HospitalLayer.jsx, etc.) so API responses look consistent with what the
frontend showed before this backend existed.

Usage: python3 seed_data.py [--db-path geo.db]
"""
import argparse
import json

from spatial_api import SpatialDB

TRAFFIC = [
    {"name": "چهارراه غزی", "lat": 27.2158, "lng": 56.2808, "level": "heavy", "delay_min": 15, "speed_kmh": 8},
    {"name": "میدان سپاه", "lat": 27.2200, "lng": 56.2850, "level": "heavy", "delay_min": 12, "speed_kmh": 10},
    {"name": "بلوار امام خمینی", "lat": 27.2180, "lng": 56.2750, "level": "medium", "delay_min": 8, "speed_kmh": 25},
    {"name": "پل خواجو", "lat": 27.2250, "lng": 56.2900, "level": "light", "delay_min": 3, "speed_kmh": 40},
    {"name": "سه‌راه ایسین", "lat": 27.2100, "lng": 56.2700, "level": "heavy", "delay_min": 20, "speed_kmh": 5},
]

CAMERAS = [
    {"code": "ba-001", "name": "چهارراه غزی", "lat": 27.2158, "lng": 56.2808, "status": "active", "types": ["traffic-light", "speed"]},
    {"code": "ba-002", "name": "میدان سپاه", "lat": 27.2200, "lng": 56.2850, "status": "active", "types": ["traffic-light"]},
    {"code": "ba-003", "name": "بلوار امام خمینی", "lat": 27.2180, "lng": 56.2750, "status": "active", "types": ["speed"]},
    {"code": "ba-004", "name": "پل خواجو", "lat": 27.2250, "lng": 56.2900, "status": "installing", "types": ["speed", "plate"]},
]

HOSPITALS = [
    {"name": "بیمارستان شهید محمدی", "lat": 27.2158, "lng": 56.2808, "type": "general", "beds": 350, "emergency": 1, "phone": "۰۷۶-۳۳۳۳۲۰۰۰", "address": "بلوار امام خمینی"},
    {"name": "بیمارستان کودکان", "lat": 27.2180, "lng": 56.2750, "type": "pediatric", "beds": 200, "emergency": 1, "phone": "۰۷۶-۳۳۳۳۳۰۰۰", "address": "خیابان شریعتی"},
    {"name": "بیمارستان خلیج فارس", "lat": 27.2200, "lng": 56.2850, "type": "specialized", "beds": 250, "emergency": 1, "phone": "۰۷۶-۳۳۳۳۴۰۰۰", "address": "بلوار امام حسین"},
]

FUEL_STATIONS = [
    {"name": "پمپ بنزین آزادی", "lat": 27.2158, "lng": 56.2808, "gasoline": 1, "cng": 1, "diesel": 1, "hours": "۲۴ ساعته"},
    {"name": "پمپ بنزین ساحلی", "lat": 27.2200, "lng": 56.2850, "gasoline": 1, "cng": 1, "diesel": 0, "hours": "۲۴ ساعته"},
    {"name": "پمپ بنزین بندر", "lat": 27.2180, "lng": 56.2750, "gasoline": 1, "cng": 0, "diesel": 1, "hours": "۲۴ ساعته"},
]

POIS = [
    {"category": "tourism", "name": "جزیره هرمز", "lat": 27.0800, "lng": 56.4500, "description": "جزیره رنگین‌کمان با خاک سرخ خوراکی"},
    {"category": "tourism", "name": "ساحل سورو", "lat": 27.2158, "lng": 56.2600, "description": "ساحل زیبا با غروب بی‌نظیر"},
    {"category": "tourism", "name": "دره ستارگان", "lat": 26.9500, "lng": 55.4700, "description": "ژئوپارک جهانی یونسکو"},
]


def seed(db_path: str) -> None:
    with SpatialDB(db_path) as db:
        for row in TRAFFIC:
            db.insert("traffic", **row)
        for row in CAMERAS:
            db.insert("cameras", **row)
        for row in HOSPITALS:
            db.insert("hospitals", **row)
        for row in FUEL_STATIONS:
            db.insert("fuel_stations", **row)
        for row in POIS:
            db.insert("pois", **row)

    print(
        f"Seeded {len(TRAFFIC)} traffic, {len(CAMERAS)} cameras, "
        f"{len(HOSPITALS)} hospitals, {len(FUEL_STATIONS)} fuel stations, "
        f"{len(POIS)} POIs into {db_path}"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed geo.db with sample Hormozgan data")
    parser.add_argument("--db-path", default="geo.db")
    args = parser.parse_args()
    seed(args.db_path)
