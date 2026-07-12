# HDP geo.db — Phase 1: SQLite R-Tree Spatial Indexing

Pure stdlib (Python 3, `sqlite3`, `http.server`) — no PostGIS, no Flask,
no extra pip installs. Runs on Termux, a VPS, or cPanel Python hosting.

## Why R-Tree instead of PostGIS

HDP's `geo.db` already lives in the 8-database SQLite split. SQLite ships
its own R-Tree virtual-table module (verified working in this build — see
`migrate.py`'s startup check). For a province-scale dataset (Hormozgan, not
a global dataset), R-Tree bbox-prefilter + haversine-in-Python covers
nearby/bbox/nearest-k queries without adding PostgreSQL as a dependency. If
HDP ever needs true polygon/spatial-join workloads at large scale, SpatiaLite
is the next step up **within the SQLite family** — PostGIS should only enter
the picture if that turns out to be insufficient.

## Files

| File | Purpose |
|---|---|
| `schema.sql` | Tables + matching `_rtree` shadow tables + sync triggers |
| `migrate.py` | Creates/upgrades `geo.db`, verifies R-Tree is available |
| `spatial_api.py` | `SpatialDB` class: `query_bbox`, `query_radius`, `query_nearest`, `insert` |
| `seed_data.py` | Sample Hormozgan data (matches the frontend's old fallback arrays) |
| `server.py` | stdlib `http.server` REST API matching `mapApi.js`'s expected endpoints |

## Setup

```bash
cd hdp-geo-backend
python3 migrate.py --db-path geo.db
python3 seed_data.py --db-path geo.db      # optional, sample data for dev
HDP_API_KEY=your-secret-here python3 server.py
```

Environment variables (`server.py`):
- `HDP_GEO_DB` — path to geo.db (default `geo.db`)
- `HDP_GEO_PORT` — port (default `8000`)
- `HDP_API_KEY` — if set, requests must send `X-API-Key: <value>`. **Unset =
  no auth**, which is fine for `localhost` dev only — the earlier HDP audit
  flagged an unauthenticated open server before, so don't skip this in
  production.
- `HDP_ALLOWED_ORIGIN` — sets `Access-Control-Allow-Origin` to this exact
  value. Unset = no CORS headers at all (same-origin only). Do not set this
  to `*` in production.

## Endpoints (match `src/services/mapApi.js` from the frontend fix pass)

```
GET  /api/v1/map/traffic?north=&south=&east=&west=
GET  /api/v1/map/cameras?north=&south=&east=&west=
GET  /api/v1/map/hospitals?north=&south=&east=&west=
GET  /api/v1/map/fuel?north=&south=&east=&west=
GET  /api/v1/map/tourism?north=&south=&east=&west=
POST /api/v1/map/cameras/<id>/report        body: {"note": "..."}
GET  /api/v1/map/nearby?table=hospitals&lat=&lng=&radius_km=5      (radius search)
GET  /api/v1/map/nearby?table=hospitals&lat=&lng=&k=3              (nearest-k)
```

Point the frontend's `REACT_APP_API_URL` at wherever this runs
(`http://<host>:8000/api/v1` by default).

## Using `SpatialDB` directly (e.g. from other HDP scripts)

```python
from spatial_api import SpatialDB

with SpatialDB("geo.db") as db:
    nearby = db.query_radius("hospitals", lat=27.2158, lng=56.2808, radius_km=5)
    closest3 = db.query_nearest("fuel_stations", lat=27.2158, lng=56.2808, k=3)
    in_view = db.query_bbox("cameras", north=27.3, south=27.1, east=56.35, west=56.2)
    db.insert("pois", category="tourism", name="...", lat=27.1, lng=56.3)
```

## What's next (Phase 2+, per the roadmap)

- WebSocket pub/sub server — this spatial layer is what live traffic/GPS
  updates from Phase 2 will write into (`UPDATE traffic SET lat=?, lng=?,
  level=? WHERE id=?`, R-Tree stays in sync automatically via triggers).
- OSRM/GraphHopper self-hosted routing (Phase 3) can query `roads`/`roads_rtree`
  for "which roads are in this bbox" without touching the routing engine itself.
- Vector tile server (Phase 4) is independent of this and can be stood up last.

## Known limitations of this pass

- `query_radius`/`query_nearest` do the exact-distance filter in Python
  after an R-Tree bbox prefilter — fine at HDP's current data volumes, but
  if any single table grows past ~1M rows within one bbox, revisit with
  SpatiaLite's native distance functions instead.
- `server.py` is single-process, no built-in rate limiting or JWT — those
  are explicitly deferred to the "امنیت" backlog item, not part of Phase 1.
- No automated test suite yet (verified manually — see the migration/query
  smoke test in this session). A `tests/` dir with `unittest` (stdlib) is a
  good next addition before this goes further than dev.
