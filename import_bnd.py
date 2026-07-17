#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sqlite3

DB = "geo.db"
JSON_FILE = "bnd.json"

con = sqlite3.connect(DB)
cur = con.cursor()

with open(JSON_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

added = 0
updated = 0

for r in data["results"]:

    cat = r.get("cat", "")
    name = r.get("name", "بدون نام").strip()

    lat = float(r["lat"])
    lng = float(r["lon"])

    if cat == "bank":

        table = "banks"
        cols = "name,bank_name,lat,lng"
        vals = (name, name, lat, lng)

    elif cat == "hospital":

        table = "hospitals"
        cols = "name,lat,lng"
        vals = (name, lat, lng)

    elif cat == "fuel":

        table = "fuel_stations"
        cols = "name,lat,lng"
        vals = (name, lat, lng)

    elif cat == "speed_camera":

        table = "cameras"
        cols = "name,lat,lng"
        vals = (name, lat, lng)

    elif cat == "traffic_signal":

        table = "traffic"
        cols = "name,lat,lng"
        vals = (name, lat, lng)

    else:

        table = "pois"
        cols = "name,category,lat,lng"
        vals = (name, cat, lat, lng)

    cur.execute(
        f"SELECT id FROM {table} WHERE ABS(lat-?)<0.00001 AND ABS(lng-?)<0.00001 AND name=?",
        (lat, lng, name)
    )

    row = cur.fetchone()

    if row:

        updated += 1

    else:

        placeholders = ",".join(["?"] * len(vals))

        cur.execute(
            f"INSERT INTO {table} ({cols}) VALUES ({placeholders})",
            vals
        )

        added += 1

con.commit()

print("=" * 40)
print("Import Finished")
print("=" * 40)
print("Inserted :", added)
print("Existing :", updated)

con.close()
