# HDP Backend — Phase 1: Spatial Core (Production-Ready Pass)

Pure stdlib (Python 3: `sqlite3`, `http.server`, `unittest`). No PostGIS,
no Flask, no pip installs. Runs on Termux, a VPS, or cPanel Python hosting.

```
backend/
  geo/
    schema.sql       tables + R-Tree shadow tables + sync triggers
    migrate.py        creates/upgrades geo.db, verifies R-Tree is available
    spatial_api.py     SpatialDB: bbox / radius / nearest-k / insert / update / delete
    seed_data.py       sample Hormozgan data, seeded through api/*.py (dogfoods validation)
    server.py          stdlib REST server, dispatches to api/*.py
  api/
    base.py             ResourceAPI: shared validation + CRUD contract
    traffic.py           TrafficAPI
    cameras.py            CameraAPI (+ report action)
    hospitals.py           HospitalAPI
    fuel.py                  FuelAPI
    tourism.py                TourismAPI
  db/
    geo.db              (created by migrate.py, not checked in)
  tests/
    test_spatial_api.py    R-Tree query + CRUD tests
    test_api_resources.py   validation logic tests, one class per resource
    test_server.py           HTTP routing/dispatch tests (in-process, no real socket)
```

## Setup

```bash
cd backend
python3 geo/migrate.py --db-path db/geo.db --schema geo/schema.sql
python3 geo/seed_data.py --db-path db/geo.db      # optional: small hand-written sample
HDP_API_KEY=your-secret-here python3 geo/server.py
```

`db/geo.db` in this delivery is **already populated** with the real scrape
(`all_hormozgan.json`, 16,593 records) via `geo/import_osm_geodata.py` — see
"Real data import" below. Delete/re-migrate it if you want a clean slate.

### Real data import

```bash
python3 geo/import_osm_geodata.py /path/to/all_hormozgan.json --db-path db/geo.db
```

Routes each record by its OSM `cat`:
- `hospital` → `hospitals` table (`type` defaults to `general` — OSM doesn't distinguish general/pediatric/specialized)
- `fuel` → `fuel_stations` table (`gasoline` defaults `True`, `cng`/`diesel` default `False` — unknown from OSM tags alone)
- everything else → `pois` table via the new generic `PoiAPI`, `category` = the OSM tag verbatim (mosque, school, park, market, police, pharmacy, museum, attraction, ...)

Last run: **16,593 imported, 0 skipped, 0.8s** (batched commits, not one
commit per row). By-category breakdown printed at the end of the run.

**Known, deliberately-not-"fixed" data quality note**: ~1,490 OSM objects in
the source carry more than one category tag (e.g. a historic mosque also
tagged `attraction`). Each `(id, cat)` pair imports as its own POI row —
often legitimate, not silently deduplicated. The original OSM id is kept in
every row's `tags.osm_id` for traceability if you want to review/merge these
later.

**Fixed while wiring this up**: `TourismAPI` originally filtered on
`category='tourism'`, a value that doesn't exist anywhere in the real OSM
taxonomy (tourism sites are tagged `attraction`) — the endpoint would have
silently returned zero results against real data. Now filters on
`category='attraction'`; route path (`/api/v1/map/tourism`) is unchanged so
the frontend doesn't need updating.

Or use `run.sh` (does all three):
```bash
HDP_API_KEY=your-secret ./run.sh
```

## Running tests

```bash
cd backend
python3 -m unittest discover -s tests -v
```
44 tests, all passing as of this pass — covers R-Tree sync on insert/update/
delete, bbox correctness (inside vs. outside), radius distance + ordering,
nearest-k radius expansion, JSON/boolean field round-tripping, every
resource's validation rules (required fields, enums, type coercion,
defaults), `fixed_filters` scoping (a shared table can't leak or write
outside its category), the bulk importer against a small fixture, and full
HTTP routing including auth and malformed-JSON handling.

## API reference

Per resource in `{traffic, cameras, hospitals, fuel, tourism}`:

```
GET    /api/v1/map/<resource>?north=&south=&east=&west=      bbox list (map viewport)
GET    /api/v1/map/<resource>?lat=&lng=&radius_km=            radius search
GET    /api/v1/map/<resource>?lat=&lng=&k=                    nearest-k search
GET    /api/v1/map/<resource>/<id>                            single record
POST   /api/v1/map/<resource>            body: {...}          create (validated)
PUT    /api/v1/map/<resource>/<id>       body: {...}          partial update
DELETE /api/v1/map/<resource>/<id>                            delete
POST   /api/v1/map/cameras/<id>/report   body: {"note": ...}  camera-specific action
```

All error responses are `{"error": "..."}` with the appropriate status:
`400` validation error, `401` missing/wrong API key, `404` not found,
`500` unexpected (message withheld, logged server-side only).

Point the frontend's `REACT_APP_API_URL` at wherever this runs
(`http://<host>:8000/api/v1` by default).

## Environment variables

| Var | Default | Notes |
|---|---|---|
| `HDP_GEO_DB` | `backend/db/geo.db` | SQLite file path |
| `HDP_GEO_PORT` | `8000` | |
| `HDP_API_KEY` | unset (no auth) | required as `X-API-Key` header when set — **set this in production** |
| `HDP_ALLOWED_ORIGIN` | unset (no CORS headers) | exact origin string, never `*` in production |

## Design decisions carried over from the review

- **SQLite R-Tree, not PostGIS** — fits the existing 8-database SQLite
  split and Termux constraints. Verified this SQLite build has R-Tree
  compiled in (`migrate.py` checks and fails loudly with instructions if not).
- **Validation lives in `api/`, storage stays "dumb" in `geo/spatial_api.py`**
  — `SpatialDB` never sees a `types` list or an unvalidated enum, only
  final column names and pre-serialized values. This is what makes adding
  a sixth resource a ~15-line file instead of touching the query engine.
- **No auth/CORS wide open by default** — a prior HDP audit flagged an
  unauthenticated open CORS server; this pass makes the safe state the
  default (warns loudly instead of silently running exposed).

## Database bridge (geo.db ⟷ knowledge engine, zero data migration)

`geo/database_bridge.py` opens geo.db and `ATTACH DATABASE`s the knowledge
engine file (hdp_v2.db) onto the *same connection*, so you can `JOIN`
across both in a single SQL query. Neither file is copied, modified, or
migrated — this is purely a query-time bridge, matching the "integration
layer first, data migration later, if ever" plan.

```python
from geo.database_bridge import DatabaseBridge

with DatabaseBridge("db/geo.db", "/path/to/hdp_v2.db") as bridge:
    rows = bridge.query("""
        SELECT h.name, r.target_entity, r.weight
        FROM hospitals h
        JOIN knowledge.knowledge_relations r
          ON r.source_entity = 'hospital:' || h.name
    """)
```

Try it against your real files:
```bash
python3 geo/bridge_example.py --geo-db db/geo.db --knowledge-db /path/to/hdp_v2.db
```

**Read this before writing through the bridge** (verified against
[sqlite.org's own ATTACH docs](https://sqlite.org/lang_attach.html), not
assumed): geo.db runs in WAL mode (`PRAGMA journal_mode = WAL` in
schema.sql — confirmed on the shipped `db/geo.db`). SQLite's documentation
states transactions across multiple attached databases are only atomic *as
a set* when the main database is **not** in WAL mode. With WAL, each
individual file still commits atomically on its own, but a single
transaction writing to both geo.db and the knowledge db is not guaranteed
to land on both files together if the process dies mid-commit.

Practical takeaway:
- Reads / cross-database `JOIN`s: no caveat, fully safe — this is the
  primary use case and what's tested here.
- Writes confined to one file per transaction: safe, no different from
  using `SpatialDB` alone.
- A single transaction that must atomically write to *both* files: not
  safe over this bridge as-is. Don't build anything load-bearing on that
  until/unless it's specifically addressed (restructure to one-file-per-
  transaction, accept eventual consistency, or drop WAL on one side).

Tested: attach/detach, schema introspection, a real cross-database `JOIN`
against the actual populated `db/geo.db` (matched an imported hospital
against a synthetic knowledge_relations row), invalid-alias rejection,
missing-file error handling, idempotent `close()`. 7 tests in
`tests/test_database_bridge.py`.

**Not yet done**: wiring `api/*.py` to use the bridge instead of a plain
`SpatialDB` connection (point 3 of the integration plan) — that needs the
real `hdp_v2.db` column names confirmed first; `bridge_example.py` uses the
schema recalled from earlier sessions (`knowledge_relations.source_entity`
etc.) as a starting guess, not a verified fact.



- WebSocket pub/sub server — writes into these same tables
  (`UPDATE traffic SET lat=?, lng=?, level=? WHERE id=?` via
  `TrafficAPI.update()`); R-Tree stays in sync automatically via triggers,
  no separate indexing step needed.
- OSRM/GraphHopper self-hosted routing (Phase 3) can query `roads`/`roads_rtree`.
- Vector tile server (Phase 4) is independent and comes last.

## Known limitations of this pass

- Exact-distance filtering happens in Python after an R-Tree bbox
  prefilter — fine at current data volumes; revisit with SpatiaLite if any
  single table exceeds roughly 1M rows within one bbox.
- `server.py` is single-process with no rate limiting or JWT — deferred to
  the security backlog item, intentionally out of scope for Phase 1.
- `roads` table exists in the schema for future use but has no resource
  module yet (no live road data source at this stage).
