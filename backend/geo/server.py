#!/usr/bin/env python3
"""
server.py — minimal REST API over geo.db, pure stdlib (http.server).

Matches the endpoint contract already expected by the frontend's
src/services/mapApi.js:

    GET  /api/v1/map/traffic?north=&south=&east=&west=
    GET  /api/v1/map/cameras?north=&south=&east=&west=
    GET  /api/v1/map/hospitals?north=&south=&east=&west=
    GET  /api/v1/map/fuel?north=&south=&east=&west=
    GET  /api/v1/map/tourism?north=&south=&east=&west=
    POST /api/v1/map/cameras/<id>/report
    GET  /api/v1/map/nearby?table=&lat=&lng=&radius_km=&k=   (bonus, generic)

Deliberately NOT open by default: if HDP_API_KEY is set, every request must
send `X-API-Key: <value>` — this was flagged in a prior HDP audit as a
recurring gap ("unauthenticated open CORS server"). CORS origin is also
locked to HDP_ALLOWED_ORIGIN (default: no CORS headers at all, i.e. same-
origin only) instead of `*`.

This is intentionally a stdlib http.server, not Flask/FastAPI, to match
HDP's dependency policy. It's single-process; put it behind a real reverse
proxy (nginx) for production concurrency/TLS.
"""
import json
import os
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

from geo.spatial_api import SpatialDB

DB_PATH = os.environ.get("HDP_GEO_DB", "geo.db")
API_KEY = os.environ.get("HDP_API_KEY")  # unset = no auth (dev only — set this in production)
ALLOWED_ORIGIN = os.environ.get("HDP_ALLOWED_ORIGIN")  # unset = no CORS headers sent
PORT = int(os.environ.get("HDP_GEO_PORT", "8000"))

CAMERA_REPORT_RE = re.compile(r"^/api/v1/map/cameras/(\d+)/report$")

TABLE_BY_ROUTE = {
    "traffic": "traffic",
    "cameras": "cameras",
    "hospitals": "hospitals",
    "fuel": "fuel_stations",
    "tourism": "pois",
}


def _bbox_from_query(qs: dict):
    try:
        return dict(
            north=float(qs["north"][0]),
            south=float(qs["south"][0]),
            east=float(qs["east"][0]),
            west=float(qs["west"][0]),
        )
    except (KeyError, ValueError, IndexError):
        return None


class Handler(BaseHTTPRequestHandler):
    server_version = "HDPGeoAPI/0.1"

    def _send_json(self, status: int, payload) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        if ALLOWED_ORIGIN:
            self.send_header("Access-Control-Allow-Origin", ALLOWED_ORIGIN)
            self.send_header("Access-Control-Allow-Headers", "X-API-Key, Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def _check_auth(self) -> bool:
        if not API_KEY:
            return True
        return self.headers.get("X-API-Key") == API_KEY

    def do_OPTIONS(self):
        self.send_response(204)
        if ALLOWED_ORIGIN:
            self.send_header("Access-Control-Allow-Origin", ALLOWED_ORIGIN)
            self.send_header("Access-Control-Allow-Headers", "X-API-Key, Content-Type")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_GET(self):
        if not self._check_auth():
            self._send_json(401, {"error": "unauthorized"})
            return

        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)
        parts = parsed.path.strip("/").split("/")  # api/v1/map/<route>

        if len(parts) == 4 and parts[:3] == ["api", "v1", "map"] and parts[3] in TABLE_BY_ROUTE:
            table = TABLE_BY_ROUTE[parts[3]]
            bbox = _bbox_from_query(qs)
            with SpatialDB(DB_PATH) as db:
                if bbox:
                    rows = db.query_bbox(table, **bbox)
                else:
                    # No bbox given -> full (limited) list, useful for dev/testing
                    rows = db.query_bbox(table, north=90, south=-90, east=180, west=-180)
            self._send_json(200, rows)
            return

        if parsed.path == "/api/v1/map/nearby":
            table = qs.get("table", [""])[0]
            if table not in TABLE_BY_ROUTE.values():
                self._send_json(400, {"error": f"unknown table '{table}'"})
                return
            try:
                lat = float(qs["lat"][0])
                lng = float(qs["lng"][0])
            except (KeyError, ValueError, IndexError):
                self._send_json(400, {"error": "lat/lng required"})
                return
            radius_km = float(qs.get("radius_km", ["5"])[0])
            k = qs.get("k", [None])[0]
            with SpatialDB(DB_PATH) as db:
                if k:
                    rows = db.query_nearest(table, lat, lng, k=int(k))
                else:
                    rows = db.query_radius(table, lat, lng, radius_km=radius_km)
            self._send_json(200, rows)
            return

        self._send_json(404, {"error": "not found"})

    def do_POST(self):
        if not self._check_auth():
            self._send_json(401, {"error": "unauthorized"})
            return

        match = CAMERA_REPORT_RE.match(self.path)
        if match:
            camera_id = int(match.group(1))
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length) if length else b"{}"
            try:
                note = json.loads(body).get("note")
            except json.JSONDecodeError:
                note = None
            with SpatialDB(DB_PATH) as db:
                db._conn.execute(
                    "INSERT INTO camera_reports (camera_id, note) VALUES (?, ?)",
                    (camera_id, note),
                )
                db._conn.commit()
            self._send_json(201, {"status": "reported", "camera_id": camera_id})
            return

        self._send_json(404, {"error": "not found"})

    def log_message(self, fmt, *args):
        print(f"[hdp-geo-api] {self.address_string()} - {fmt % args}")


def main():
    if not API_KEY:
        print(
            "WARNING: HDP_API_KEY is not set — this server is running WITHOUT "
            "authentication. Set HDP_API_KEY before exposing it beyond localhost."
        )
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"HDP geo API listening on :{PORT} (db={DB_PATH})")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    main()
