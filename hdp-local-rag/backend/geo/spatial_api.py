#!/usr/bin/env python3
"""
geo/spatial_api.py — spatial query + CRUD layer over geo.db's R-Tree indexes.

Pure stdlib (sqlite3 + math + json + time). No shapely/geopandas/PostGIS.

R-Tree gives a fast bounding-box prefilter; exact great-circle distance
(haversine) is computed in Python only over the small candidate set the
R-Tree returns, then used for radius filtering / nearest-k sorting.

This module is intentionally "dumb" about field semantics (JSON encoding,
enum validation, defaults) -- that's the api/ layer's job (see api/base.py).
SpatialDB just moves already-prepared column dicts in and out of SQLite and
guarantees the R-Tree stays in sync via the triggers in schema.sql.
"""
import json
import math
import sqlite3
import time
from dataclasses import dataclass
from typing import Optional


EARTH_RADIUS_KM = 6371.0088

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
    return km / 111.32


def km_to_deg_lng(km: float, at_lat: float) -> float:
    return km / (111.32 * max(math.cos(math.radians(at_lat)), 1e-6))


def _row_to_dict(row: sqlite3.Row) -> dict:
    """Decode *_json columns back into their `types`/`tags` Python-facing
    names, and 0/1 integer flags into booleans. Purely a read-side
    convenience -- write-side field naming lives in api/base.py."""
    d = dict(row)
    for key in list(d.keys()):
        if key.endswith("_json") and d[key]:
            try:
                d[key[: -len("_json")]] = json.loads(d.pop(key))
            except (json.JSONDecodeError, TypeError):
                pass
    for key in ("emergency", "gasoline", "cng", "diesel"):
        if key in d and d[key] is not None:
            d[key] = bool(d[key])
    return d


class SpatialDBError(Exception):
    pass


@dataclass
class SpatialDB:
    db_path: str
    # False for bulk imports: caller commits explicitly (see geo/import_osm_geodata.py).
    # True (default) for the REST server: every write is its own transaction.
    autocommit: bool = True

    def __post_init__(self):
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")

    def commit(self):
        self._conn.commit()

    def close(self):
        self._conn.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def _check_table(self, table: str) -> None:
        if table not in TABLE_COLUMNS:
            raise SpatialDBError(f"unknown spatial table: {table}")

    def _columns(self, table: str) -> str:
        self._check_table(table)
        return TABLE_COLUMNS[table]

    # -- Bounding box (map viewport) ----------------------------------
    def query_bbox(self, table: str, north: float, south: float, east: float, west: float,
                    limit: int = 500, where: Optional[dict] = None) -> list:
        """`where`: optional exact-match column filters, e.g. {"category": "tourism"} --
        used so resources that share a table (like `pois`) don't leak each
        other's rows. Column names are only ever taken from TABLE_COLUMNS-
        validated callers (api/base.py), never raw user input, so this stays
        injection-safe despite the f-string."""
        cols = self._columns(table)
        select_cols = ", ".join(f"m.{c.strip()}" for c in cols.split(","))
        extra_sql = ""
        params = [north, south, east, west]
        if where:
            extra_sql = " AND " + " AND ".join(f"m.{k} = ?" for k in where)
            params += list(where.values())
        sql = f"""
            SELECT {select_cols} FROM {table} m
            JOIN {table}_rtree r ON r.id = m.id
            WHERE r.min_lat <= ? AND r.max_lat >= ?
              AND r.min_lng <= ? AND r.max_lng >= ?
              {extra_sql}
            LIMIT ?
        """
        rows = self._conn.execute(sql, (*params, limit)).fetchall()
        return [_row_to_dict(r) for r in rows]

    # -- Radius search ("nearby") --------------------------------------
    def query_radius(self, table: str, lat: float, lng: float, radius_km: float,
                      limit: Optional[int] = None, where: Optional[dict] = None) -> list:
        dlat = km_to_deg_lat(radius_km)
        dlng = km_to_deg_lng(radius_km, lat)
        candidates = self.query_bbox(
            table, north=lat + dlat, south=lat - dlat, east=lng + dlng, west=lng - dlng,
            limit=limit * 5 if limit else 2000, where=where,
        )
        results = []
        for row in candidates:
            dist = haversine_km(lat, lng, row["lat"], row["lng"])
            if dist <= radius_km:
                row["distance_km"] = round(dist, 3)
                results.append(row)
        results.sort(key=lambda r: r["distance_km"])
        return results[:limit] if limit else results

    # -- Nearest-k (expanding radius search) ----------------------------
    def query_nearest(self, table: str, lat: float, lng: float, k: int = 5,
                       max_radius_km: float = 100.0) -> list:
        radius = 2.0
        while radius <= max_radius_km:
            results = self.query_radius(table, lat, lng, radius, limit=None)
            if len(results) >= k:
                return results[:k]
            radius *= 2
        return self.query_radius(table, lat, lng, max_radius_km, limit=k)

    def get(self, table: str, obj_id: int) -> Optional[dict]:
        cols = self._columns(table)
        select_cols = ", ".join(c.strip() for c in cols.split(","))
        row = self._conn.execute(
            f"SELECT {select_cols} FROM {table} WHERE id = ?", (obj_id,)
        ).fetchone()
        return _row_to_dict(row) if row else None

    # -- Writes (R-Tree stays in sync automatically via schema triggers) -
    def insert(self, table: str, **columns) -> int:
        """`columns` must already use real DB column names (e.g. `types_json`,
        not `types`) with values pre-serialized (JSON strings, not lists)."""
        self._check_table(table)
        columns.setdefault("updated_at", int(time.time()))
        cols = ", ".join(columns.keys())
        placeholders = ", ".join("?" for _ in columns)
        cur = self._conn.execute(
            f"INSERT INTO {table} ({cols}) VALUES ({placeholders})", tuple(columns.values())
        )
        if self.autocommit:
            self._conn.commit()
        return cur.lastrowid

    def update(self, table: str, obj_id: int, **columns) -> None:
        self._check_table(table)
        if not columns:
            return
        columns["updated_at"] = int(time.time())
        set_clause = ", ".join(f"{k} = ?" for k in columns)
        cur = self._conn.execute(
            f"UPDATE {table} SET {set_clause} WHERE id = ?", (*columns.values(), obj_id)
        )
        if self.autocommit:
            self._conn.commit()
        if cur.rowcount == 0:
            raise SpatialDBError(f"{table} id={obj_id} not found")

    def delete(self, table: str, obj_id: int) -> None:
        self._check_table(table)
        cur = self._conn.execute(f"DELETE FROM {table} WHERE id = ?", (obj_id,))
        if self.autocommit:
            self._conn.commit()
        if cur.rowcount == 0:
            raise SpatialDBError(f"{table} id={obj_id} not found")
