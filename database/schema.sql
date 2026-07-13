-- geo.db schema — HDP Phase 1: Spatial Indexing with SQLite R-Tree
--
-- Design notes:
--   * Every spatial table below has a matching `<table>_rtree` virtual table
--     (SQLite's built-in R-Tree module — no extension install needed on a
--     standard SQLite build; Termux's `sqlite` package includes it).
--   * Points are stored as degenerate boxes (minLat=maxLat, minLng=maxLng)
--     so the same R-Tree machinery also works if road/zone geometries with
--     real bounding boxes are added later.
--   * AFTER INSERT/UPDATE/DELETE triggers keep each `_rtree` table in sync
--     automatically — callers never touch the R-Tree tables directly.
--   * R-Tree gives a fast *bounding-box* prefilter only. Exact distance
--     (haversine) filtering/sorting happens in spatial_api.py after the
--     R-Tree narrows candidates down — this is the standard SQLite pattern
--     since R-Tree has no notion of "km".

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

-- ─────────────────────────────────────────────────────────────────────────
-- Generic POIs (tourism sites, landmarks, etc. — anything not covered by a
-- dedicated table below)
-- ─────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS pois (
    id          INTEGER PRIMARY KEY,
    category    TEXT NOT NULL,           -- 'tourism', 'landmark', ...
    name        TEXT NOT NULL,
    lat         REAL NOT NULL,
    lng         REAL NOT NULL,
    description TEXT,
    tags_json   TEXT,                    -- freeform JSON for extra fields
    tenant_uuid TEXT,                    -- multi-tenant scoping, matches search.db convention
    updated_at  INTEGER NOT NULL DEFAULT (strftime('%s','now'))
);
CREATE INDEX IF NOT EXISTS idx_pois_category ON pois(category);

CREATE VIRTUAL TABLE IF NOT EXISTS pois_rtree USING rtree(
    id, min_lat, max_lat, min_lng, max_lng
);

CREATE TRIGGER IF NOT EXISTS pois_ai AFTER INSERT ON pois BEGIN
    INSERT INTO pois_rtree(id, min_lat, max_lat, min_lng, max_lng)
    VALUES (new.id, new.lat, new.lat, new.lng, new.lng);
END;
CREATE TRIGGER IF NOT EXISTS pois_au AFTER UPDATE OF lat, lng ON pois BEGIN
    UPDATE pois_rtree SET min_lat = new.lat, max_lat = new.lat,
                           min_lng = new.lng, max_lng = new.lng
    WHERE id = new.id;
END;
CREATE TRIGGER IF NOT EXISTS pois_ad AFTER DELETE ON pois BEGIN
    DELETE FROM pois_rtree WHERE id = old.id;
END;

-- ─────────────────────────────────────────────────────────────────────────
-- Traffic (live-updated by the WebSocket layer in Phase 2 — this table
-- always holds the *current* snapshot per segment, not history)
-- ─────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS traffic (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    lat         REAL NOT NULL,
    lng         REAL NOT NULL,
    level       TEXT NOT NULL CHECK (level IN ('light','medium','heavy')),
    speed_kmh   REAL,
    delay_min   REAL,
    updated_at  INTEGER NOT NULL DEFAULT (strftime('%s','now'))
);

CREATE VIRTUAL TABLE IF NOT EXISTS traffic_rtree USING rtree(
    id, min_lat, max_lat, min_lng, max_lng
);

CREATE TRIGGER IF NOT EXISTS traffic_ai AFTER INSERT ON traffic BEGIN
    INSERT INTO traffic_rtree(id, min_lat, max_lat, min_lng, max_lng)
    VALUES (new.id, new.lat, new.lat, new.lng, new.lng);
END;
CREATE TRIGGER IF NOT EXISTS traffic_au AFTER UPDATE OF lat, lng ON traffic BEGIN
    UPDATE traffic_rtree SET min_lat = new.lat, max_lat = new.lat,
                              min_lng = new.lng, max_lng = new.lng
    WHERE id = new.id;
END;
CREATE TRIGGER IF NOT EXISTS traffic_ad AFTER DELETE ON traffic BEGIN
    DELETE FROM traffic_rtree WHERE id = old.id;
END;

-- ─────────────────────────────────────────────────────────────────────────
-- Cameras
-- ─────────────────────────────────────────────────────────────────────────
-- R-Tree requires an INTEGER key, so cameras use a normal integer PK like
-- every other table here; the human-readable frontend id (e.g. "ba-001")
-- lives in `code` instead. This avoids a separate id-mapping table.
CREATE TABLE IF NOT EXISTS cameras (
    id          INTEGER PRIMARY KEY,
    code        TEXT UNIQUE NOT NULL,    -- e.g. 'ba-001' (matches existing frontend ids)
    name        TEXT NOT NULL,
    lat         REAL NOT NULL,
    lng         REAL NOT NULL,
    status      TEXT NOT NULL CHECK (status IN ('active','installing','pending')),
    types_json  TEXT,                    -- JSON array: ["speed","plate",...]
    updated_at  INTEGER NOT NULL DEFAULT (strftime('%s','now'))
);

CREATE VIRTUAL TABLE IF NOT EXISTS cameras_rtree USING rtree(
    id, min_lat, max_lat, min_lng, max_lng
);
CREATE TRIGGER IF NOT EXISTS cameras_ai AFTER INSERT ON cameras BEGIN
    INSERT INTO cameras_rtree(id, min_lat, max_lat, min_lng, max_lng)
    VALUES (new.id, new.lat, new.lat, new.lng, new.lng);
END;
CREATE TRIGGER IF NOT EXISTS cameras_au AFTER UPDATE OF lat, lng ON cameras BEGIN
    UPDATE cameras_rtree SET min_lat = new.lat, max_lat = new.lat,
                              min_lng = new.lng, max_lng = new.lng
    WHERE id = new.id;
END;
CREATE TRIGGER IF NOT EXISTS cameras_ad AFTER DELETE ON cameras BEGIN
    DELETE FROM cameras_rtree WHERE id = old.id;
END;

CREATE TABLE IF NOT EXISTS camera_reports (
    id          INTEGER PRIMARY KEY,
    camera_id   INTEGER NOT NULL REFERENCES cameras(id) ON DELETE CASCADE,
    reported_at INTEGER NOT NULL DEFAULT (strftime('%s','now')),
    note        TEXT
);

-- ─────────────────────────────────────────────────────────────────────────
-- Hospitals
-- ─────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS hospitals (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    lat         REAL NOT NULL,
    lng         REAL NOT NULL,
    type        TEXT NOT NULL CHECK (type IN ('general','pediatric','specialized')),
    beds        INTEGER,
    emergency   INTEGER NOT NULL DEFAULT 1,   -- boolean 0/1
    phone       TEXT,
    address     TEXT,
    updated_at  INTEGER NOT NULL DEFAULT (strftime('%s','now'))
);

CREATE VIRTUAL TABLE IF NOT EXISTS hospitals_rtree USING rtree(
    id, min_lat, max_lat, min_lng, max_lng
);
CREATE TRIGGER IF NOT EXISTS hospitals_ai AFTER INSERT ON hospitals BEGIN
    INSERT INTO hospitals_rtree(id, min_lat, max_lat, min_lng, max_lng)
    VALUES (new.id, new.lat, new.lat, new.lng, new.lng);
END;
CREATE TRIGGER IF NOT EXISTS hospitals_au AFTER UPDATE OF lat, lng ON hospitals BEGIN
    UPDATE hospitals_rtree SET min_lat = new.lat, max_lat = new.lat,
                                min_lng = new.lng, max_lng = new.lng
    WHERE id = new.id;
END;
CREATE TRIGGER IF NOT EXISTS hospitals_ad AFTER DELETE ON hospitals BEGIN
    DELETE FROM hospitals_rtree WHERE id = old.id;
END;

-- ─────────────────────────────────────────────────────────────────────────
-- Fuel stations
-- ─────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS fuel_stations (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    lat         REAL NOT NULL,
    lng         REAL NOT NULL,
    gasoline    INTEGER NOT NULL DEFAULT 1,
    cng         INTEGER NOT NULL DEFAULT 0,
    diesel      INTEGER NOT NULL DEFAULT 0,
    hours       TEXT,
    updated_at  INTEGER NOT NULL DEFAULT (strftime('%s','now'))
);

CREATE VIRTUAL TABLE IF NOT EXISTS fuel_stations_rtree USING rtree(
    id, min_lat, max_lat, min_lng, max_lng
);
CREATE TRIGGER IF NOT EXISTS fuel_ai AFTER INSERT ON fuel_stations BEGIN
    INSERT INTO fuel_stations_rtree(id, min_lat, max_lat, min_lng, max_lng)
    VALUES (new.id, new.lat, new.lat, new.lng, new.lng);
END;
CREATE TRIGGER IF NOT EXISTS fuel_au AFTER UPDATE OF lat, lng ON fuel_stations BEGIN
    UPDATE fuel_stations_rtree SET min_lat = new.lat, max_lat = new.lat,
                                    min_lng = new.lng, max_lng = new.lng
    WHERE id = new.id;
END;
CREATE TRIGGER IF NOT EXISTS fuel_ad AFTER DELETE ON fuel_stations BEGIN
    DELETE FROM fuel_stations_rtree WHERE id = old.id;
END;

-- ─────────────────────────────────────────────────────────────────────────
-- Roads (bounding-box only for now — full route geometry stays with the
-- OSRM/GraphHopper engine in Phase 3; this table is for road-name lookups
-- and future "which roads pass through this bbox" queries)
-- ─────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS roads (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    min_lat     REAL NOT NULL,
    max_lat     REAL NOT NULL,
    min_lng     REAL NOT NULL,
    max_lng     REAL NOT NULL,
    road_class  TEXT,                    -- 'primary','secondary','residential',...
    updated_at  INTEGER NOT NULL DEFAULT (strftime('%s','now'))
);

CREATE VIRTUAL TABLE IF NOT EXISTS roads_rtree USING rtree(
    id, min_lat, max_lat, min_lng, max_lng
);
CREATE TRIGGER IF NOT EXISTS roads_ai AFTER INSERT ON roads BEGIN
    INSERT INTO roads_rtree(id, min_lat, max_lat, min_lng, max_lng)
    VALUES (new.id, new.min_lat, new.max_lat, new.min_lng, new.max_lng);
END;
CREATE TRIGGER IF NOT EXISTS roads_au AFTER UPDATE OF min_lat, max_lat, min_lng, max_lng ON roads BEGIN
    UPDATE roads_rtree SET min_lat = new.min_lat, max_lat = new.max_lat,
                            min_lng = new.min_lng, max_lng = new.max_lng
    WHERE id = new.id;
END;
CREATE TRIGGER IF NOT EXISTS roads_ad AFTER DELETE ON roads BEGIN
    DELETE FROM roads_rtree WHERE id = old.id;
END;
