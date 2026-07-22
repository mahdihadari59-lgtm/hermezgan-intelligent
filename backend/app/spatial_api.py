#!/usr/bin/env python3
"""
spatial_api.py — spatial query layer over geo.db's R-Tree indexes.

Pure stdlib (sqlite3 + math + json). No shapely/geopandas/PostGIS.

R-Tree gives a fast bounding-box prefilter; exact great-circle distance
(haversine) is computed in Python only over the small candidate set the
R-Tree returns, then used for radius filtering / nearest-k sorting. This is
the standard, documented pattern for using SQLite's R-Tree module for
"distance" queries, since R-Tree itself only knows about boxes.

Usage:
    from spatial_api import SpatialDB

    db = SpatialDB("geo.db")
    cameras_in_view = db.query_bbox("cameras", north=27.30, south=27.10, east=56.35, west=56.20)
    nearby_hospitals = db.query_radius("hospitals", lat=27.2158, lng=56.2808, radius_km=5)
    closest_fuel = db.query_nearest("fuel_stations", lat=27.2158, lng=56.2808, k=3)
"""
import json
import math
import sqlite3
from dataclasses import dataclass
from typing import Optional


EARTH_RADIUS_KM = 6371.0088

# Table registry: which columns to select back from the main table, and
# whether the table's PK matches its rtree table's `id` 1:1 (true for every
# table in schema.sql after the cameras fix).
TABLE_COLUMNS = {
    "pois": "id, category, name, lat, lng, description, tags_json, updated_at",
    "traffic": "id, name, lat, lng, level, speed_kmh, delay_min, updated_at",
    "cameras": "id, code, name, lat, lng, status, types_json, updated_at",
    "hospitals": "id, name, lat, lng, type, beds, emergency, phone, address, updated_at",
    "fuel_stations": "id, name, lat, lng, gasoline, cng, diesel, hours, updated_at",
}


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def km_to_deg_lat(km: float) -> float:
    return km / 111.32  # ~constant everywhere


def km_to_deg_lng(km: float, at_lat: float) -> float:
    return km / (111.32 * max(math.cos(math.radians(at_lat)), 1e-6))


def _row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    for key in ("tags_json", "types_json"):
        if key in d and d[key]:
            try:
                d[key.replace("_json", "")] = json.loads(d.pop(key))
            except (json.JSONDecodeError, TypeError):
                pass
    for key in ("emergency", "gasoline", "cng", "diesel"):
        if key in d and d[key] is not None:
            d[key] = bool(d[key])
    return d


@dataclass
class SpatialDB:
    db_path: str

    def __post_init__(self):
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")

    def close(self):
        self._conn.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def _columns(self, table: str) -> str:
        if table not in TABLE_COLUMNS:
            raise ValueError(f"Unknown spatial table: {table}")
        return TABLE_COLUMNS[table]

    # ── Bounding box (map viewport) ────────────────────────────────────
    def query_bbox(self, table: str, north: float, south: float, east: float, west: float,
                    limit: int = 500) -> list:
        cols = self._columns(table)
        sql = f"""
            SELECT m.* FROM {table} m
            JOIN {table}_rtree r ON r.id = m.id
            WHERE r.min_lat <= ? AND r.max_lat >= ?
              AND r.min_lng <= ? AND r.max_lng >= ?
            LIMIT ?
        """
        # Replace m.* with explicit columns for a stable, documented shape
        sql = sql.replace("m.*", ", ".join(f"m.{c.strip()}" for c in cols.split(",")))
        rows = self._conn.execute(sql, (north, south, east, west, limit)).fetchall()
        return [_row_to_dict(r) for r in rows]

    # ── Radius search ("nearby") ───────────────────────────────────────
    def query_radius(self, table: str, lat: float, lng: float, radius_km: float,
                      limit: Optional[int] = None) -> list:
        dlat = km_to_deg_lat(radius_km)
        dlng = km_to_deg_lng(radius_km, lat)
        candidates = self.query_bbox(
            table, north=lat + dlat, south=lat - dlat, east=lng + dlng, west=lng - dlng,
            limit=limit * 5 if limit else 2000,
        )
        results = []
        for row in candidates:
            dist = haversine_km(lat, lng, row["lat"], row["lng"])
            if dist <= radius_km:
                row["distance_km"] = round(dist, 3)
                results.append(row)
        results.sort(key=lambda r: r["distance_km"])
        return results[:limit] if limit else results

    # ── Nearest-k (expanding radius search) ────────────────────────────
    def query_nearest(self, table: str, lat: float, lng: float, k: int = 5,
                       max_radius_km: float = 100.0) -> list:
        radius = 2.0
        while radius <= max_radius_km:
            results = self.query_radius(table, lat, lng, radius, limit=None)
            if len(results) >= k:
                return results[:k]
            radius *= 2
        # last attempt at the max radius, return whatever we found
        return self.query_radius(table, lat, lng, max_radius_km, limit=k)

    # ── Simple insert helper (keeps R-Tree in sync via schema triggers) ─
    def insert(self, table: str, **fields) -> int:
        if table not in TABLE_COLUMNS:
            raise ValueError(f"Unknown spatial table: {table}")
        for json_field in ("tags", "types"):
            if json_field in fields:
                fields[f"{json_field}_json"] = json.dumps(fields.pop(json_field), ensure_ascii=False)
        cols = ", ".join(fields.keys())
        placeholders = ", ".join("?" for _ in fields)
        cur = self._conn.execute(
            f"INSERT INTO {table} ({cols}) VALUES ({placeholders})", tuple(fields.values())
        )
        self._conn.commit()
        return cur.lastrowid
