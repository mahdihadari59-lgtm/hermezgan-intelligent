#!/usr/bin/env python3
"""
geo/import_osm_geodata.py — bulk-import the OSM/Neshan geodata scrape
(all_hormozgan.json) into geo.db.

Mapping:
  cat == 'hospital'  -> hospitals table (via HospitalAPI)  -- type defaults to 'general'
                         (OSM doesn't distinguish general/pediatric/specialized)
  cat == 'fuel'       -> fuel_stations table (via FuelAPI)  -- gasoline defaults True,
                         cng/diesel default False (unknown from OSM tags alone)
  everything else      -> pois table (via PoiAPI), category = cat verbatim
                         (mosque, school, park, market, police, pharmacy, museum, ...)

Known data-quality note, intentionally NOT "fixed" here (per conversation --
ignore for this import): ~1,490 OSM objects in the source file appear under
more than one category (e.g. a mosque also tagged 'attraction', an island
also tagged 'coastline'). Each (id, cat) pair is imported as its own POI
row -- this is often legitimate (a historic mosque genuinely is also a
tourist attraction) and is left for a future explicit review pass rather
than silently deduplicated. The original OSM id is preserved in `tags` on
every row for traceability.

Usage:
    python3 import_osm_geodata.py /path/to/all_hormozgan.json \\
        [--db-path ../db/geo.db] [--batch-size 500]
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # backend/

from geo.spatial_api import SpatialDB
from api.hospitals import HospitalAPI
from api.fuel import FuelAPI
from api.poi import PoiAPI
from api.base import ValidationError

# Hormozgan province rough bounding box -- used only to flag (not drop)
# suspicious coordinates in the summary. Hajiabad/Bastak legitimately reach
# up to ~28.5N, so this is intentionally generous rather than a hard filter.
LAT_MIN, LAT_MAX = 24.5, 29.0
LON_MIN, LON_MAX = 52.5, 59.5


def _hospital_payload(rec):
    return {"name": rec["name"] or "بدون نام", "lat": rec["lat"], "lng": rec["lon"], "type": "general"}


def _fuel_payload(rec):
    return {"name": rec["name"] or "بدون نام", "lat": rec["lat"], "lng": rec["lon"]}


def _poi_payload(rec):
    return {
        "category": rec["cat"],
        "name": rec["name"] or "بدون نام",
        "lat": rec["lat"],
        "lng": rec["lon"],
        "tags": {"osm_id": rec["id"]},
    }


ROUTES = {
    "hospital": (HospitalAPI, _hospital_payload),
    "fuel": (FuelAPI, _fuel_payload),
}


def import_file(json_path: str, db_path: str, batch_size: int = 500) -> dict:
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)
    records = data.get("results", data if isinstance(data, list) else [])

    stats = {"imported": 0, "skipped": 0, "by_category": {}, "errors": []}
    suspicious_coords = 0

    db = SpatialDB(db_path, autocommit=False)
    started = time.time()
    try:
        for i, rec in enumerate(records, 1):
            cat = rec.get("cat", "unknown")
            lat, lon = rec.get("lat"), rec.get("lon")
            if lat is None or lon is None:
                stats["skipped"] += 1
                continue
            if not (LAT_MIN <= lat <= LAT_MAX and LON_MIN <= lon <= LON_MAX):
                suspicious_coords += 1  # still imported -- just flagged in the summary

            api_cls, payload_fn = ROUTES.get(cat, (PoiAPI, _poi_payload))
            payload = payload_fn(rec)
            try:
                api_cls.create(db, payload)
                stats["imported"] += 1
                stats["by_category"][cat] = stats["by_category"].get(cat, 0) + 1
            except ValidationError as e:
                stats["skipped"] += 1
                stats["errors"].append(f"{rec.get('id')}: {e.message}")

            if i % batch_size == 0:
                db.commit()
                print(f"  ...{i}/{len(records)}", end="\r")

        db.commit()
    finally:
        db.close()

    elapsed = time.time() - started
    print(f"\nDone in {elapsed:.1f}s")
    print(f"Imported: {stats['imported']}  Skipped: {stats['skipped']}  "
          f"Suspicious coords (imported anyway): {suspicious_coords}")
    print("By category (top 15):")
    for cat, n in sorted(stats["by_category"].items(), key=lambda x: -x[1])[:15]:
        print(f"  {cat:25s} {n}")
    if stats["errors"]:
        print(f"\n{len(stats['errors'])} validation errors, first 10:")
        for e in stats["errors"][:10]:
            print(" ", e)

    return stats


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import OSM geodata scrape into geo.db")
    parser.add_argument("json_path", help="Path to all_hormozgan.json (or a per-category export)")
    parser.add_argument("--db-path", default="../db/geo.db")
    parser.add_argument("--batch-size", type=int, default=500)
    args = parser.parse_args()
    import_file(args.json_path, args.db_path, args.batch_size)
