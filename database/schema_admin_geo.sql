-- ════════════════════════════════════════════════════════════════════════════
-- Administrative Geography Schema - Hormozgan Province
-- ════════════════════════════════════════════════════════════════════════════
-- Extension to geo.db schema for county and island management
-- Includes R-Tree spatial indexing for efficient geographical queries

-- ────────────────────────────────────────────────────────────────────────────
-- COUNTIES TABLE
-- ────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS geo_counties (
    id              INTEGER PRIMARY KEY,
    name            TEXT NOT NULL UNIQUE,           -- Persian name
    name_en         TEXT,                           -- English name
    province        TEXT NOT NULL DEFAULT 'هرمزگان',
    center          TEXT,                           -- Center city name
    lat             REAL NOT NULL,
    lng             REAL NOT NULL,
    aliases_json    TEXT,                           -- JSON array of alternative names
    area_km2        REAL,
    population      INTEGER,
    description     TEXT,
    updated_at      INTEGER NOT NULL DEFAULT (strftime('%s','now'))
);

CREATE INDEX IF NOT EXISTS idx_geo_counties_name ON geo_counties(name);
CREATE INDEX IF NOT EXISTS idx_geo_counties_name_en ON geo_counties(name_en);
CREATE INDEX IF NOT EXISTS idx_geo_counties_latlng ON geo_counties(lat, lng);

CREATE VIRTUAL TABLE IF NOT EXISTS geo_counties_rtree USING rtree(
    id, min_lat, max_lat, min_lng, max_lng
);

CREATE TRIGGER IF NOT EXISTS geo_counties_ai AFTER INSERT ON geo_counties BEGIN
    INSERT INTO geo_counties_rtree(id, min_lat, max_lat, min_lng, max_lng)
    VALUES (new.id, new.lat, new.lat, new.lng, new.lng);
END;

CREATE TRIGGER IF NOT EXISTS geo_counties_au AFTER UPDATE OF lat, lng ON geo_counties BEGIN
    UPDATE geo_counties_rtree SET min_lat = new.lat, max_lat = new.lat,
                                   min_lng = new.lng, max_lng = new.lng
    WHERE id = new.id;
END;

CREATE TRIGGER IF NOT EXISTS geo_counties_ad AFTER DELETE ON geo_counties BEGIN
    DELETE FROM geo_counties_rtree WHERE id = old.id;
END;

-- ────────────────────────────────────────────────────────────────────────────
-- ISLANDS TABLE
-- ────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS geo_islands (
    id              INTEGER PRIMARY KEY,
    name            TEXT NOT NULL UNIQUE,           -- Persian name
    name_en         TEXT,                           -- English name
    county_id       INTEGER NOT NULL REFERENCES geo_counties(id) ON DELETE CASCADE,
    lat             REAL NOT NULL,
    lng             REAL NOT NULL,
    aliases_json    TEXT,                           -- JSON array of alternative names
    area_km2        REAL,
    population      INTEGER,
    type            TEXT DEFAULT 'island',
    description     TEXT,
    updated_at      INTEGER NOT NULL DEFAULT (strftime('%s','now'))
);

CREATE INDEX IF NOT EXISTS idx_geo_islands_name ON geo_islands(name);
CREATE INDEX IF NOT EXISTS idx_geo_islands_name_en ON geo_islands(name_en);
CREATE INDEX IF NOT EXISTS idx_geo_islands_county ON geo_islands(county_id);
CREATE INDEX IF NOT EXISTS idx_geo_islands_latlng ON geo_islands(lat, lng);

CREATE VIRTUAL TABLE IF NOT EXISTS geo_islands_rtree USING rtree(
    id, min_lat, max_lat, min_lng, max_lng
);

CREATE TRIGGER IF NOT EXISTS geo_islands_ai AFTER INSERT ON geo_islands BEGIN
    INSERT INTO geo_islands_rtree(id, min_lat, max_lat, min_lng, max_lng)
    VALUES (new.id, new.lat, new.lat, new.lng, new.lng);
END;

CREATE TRIGGER IF NOT EXISTS geo_islands_au AFTER UPDATE OF lat, lng ON geo_islands BEGIN
    UPDATE geo_islands_rtree SET min_lat = new.lat, max_lat = new.lat,
                                  min_lng = new.lng, max_lng = new.lng
    WHERE id = new.id;
END;

CREATE TRIGGER IF NOT EXISTS geo_islands_ad AFTER DELETE ON geo_islands BEGIN
    DELETE FROM geo_islands_rtree WHERE id = old.id;
END;

-- ────────────────────────────────────────────────────────────────────────────
-- COUNTIES DATA - Hormozgan Province
-- ────────────────────────────────────────────────────────────────────────────
INSERT OR REPLACE INTO geo_counties (id, name, center, lat, lng, aliases_json)
VALUES
    (1, 'بندرعباس', 'بندرعباس', 27.1842, 56.2893, '["Bandar Abbas","Bندر عباس"]'),
    (2, 'میناب', 'میناب', 27.1506, 57.0753, '["Minab"]'),
    (3, 'قشم', 'قشم', 26.7833, 55.8667, '["Qeshm"]'),
    (4, 'بندرلنگه', 'بندرلنگه', 26.5579, 54.8807, '["Bandar Lengeh"]'),
    (5, 'پارسیان', 'پارسیان', 27.2082, 53.0351, '["Parsian"]'),
    (6, 'حاجی‌آباد', 'حاجی‌آباد', 28.3072, 55.8985, '["Hajiabad"]'),
    (7, 'رودان', 'رودان', 27.5333, 57.1167, '["Rudan"]'),
    (8, 'بشاگرد', 'سردشت', 26.3483, 57.7567, '["Bashagard","Sardasht"]'),
    (9, 'سیریک', 'بندر سیریک', 26.5201, 57.1072, '["Sirik","Bandar Sirik"]'),
    (10, 'جاسک', 'جاسک', 25.6436, 57.7746, '["Jask"]'),
    (11, 'خمیر', 'بندر خمیر', 26.9519, 55.5855, '["Khamir","Bandar Khamir"]'),
    (12, 'بستک', 'بستک', 27.1977, 54.3626, '["Bastak"]'),
    (13, 'ابوموسی', 'ابوموسی', 25.8778, 55.033, '["Abu Musa"]');

-- ────────────────────────────────────────────────────────────────────────────
-- ISLANDS DATA - Hormozgan Province
-- ────────────────────────────────────────────────────────────────────────────
INSERT OR REPLACE INTO geo_islands (id, name, county_id, lat, lng, aliases_json, type)
VALUES
    -- Qeshm County Islands
    (1, 'قشم', 3, 26.8264, 55.9355, '["Qeshm"]', 'island'),
    (2, 'هرمز', 3, 27.0649, 56.4644, '["Hormuz"]', 'island'),
    (3, 'هنگام', 3, 26.6485, 55.8794, '["Hengam"]', 'island'),
    (4, 'لارک', 3, 26.8558, 56.364, '["Larak"]', 'island'),
    
    -- Bandar Lengeh County Islands
    (5, 'کیش', 4, 26.5439, 54.0136, '["Kish"]', 'island'),
    (6, 'لاوان', 4, 26.8058, 53.268, '["Lavan"]', 'island'),
    (7, 'هندورابی', 4, 26.6888, 53.6226, '["Hendurabi"]', 'island'),
    (8, 'شیدور', 4, 26.7919, 53.4088, '["Shidvar"]', 'island'),
    
    -- Abu Musa County Islands
    (9, 'ابوموسی', 13, 25.8778, 55.033, '["Abu Musa"]', 'island'),
    (10, 'تنب بزرگ', 13, 26.2592, 55.3158, '["Greater Tunb"]', 'island'),
    (11, 'تنب کوچک', 13, 26.2416, 55.1476, '["Lesser Tunb"]', 'island'),
    (12, 'سیری', 13, 25.9128, 54.5243, '["Sirri"]', 'island'),
    (13, 'فارور', 13, 26.2926, 54.5018, '["Faror","Farur"]', 'island'),
    (14, 'فارور کوچک', 13, 26.1186, 54.4408, '["Little Faror","Faror-e Kuchak"]', 'island');

-- ────────────────────────────────────────────────────────────────────────────
-- VIEW: All Geographic Points (Counties + Islands)
-- ────────────────────────────────────────────────────────────────────────────
CREATE VIEW IF NOT EXISTS geo_all_points AS
SELECT 
    'county' as kind,
    'county-' || id as id,
    id as entity_id,
    name as name,
    center,
    lat,
    lng,
    NULL as county_id,
    aliases_json,
    description
FROM geo_counties
UNION ALL
SELECT 
    'island' as kind,
    'island-' || gi.id as id,
    gi.id as entity_id,
    gi.name as name,
    gc.name as center,
    gi.lat,
    gi.lng,
    gi.county_id,
    gi.aliases_json,
    gi.description
FROM geo_islands gi
JOIN geo_counties gc ON gi.county_id = gc.id;

-- ────────────────────────────────────────────────────────────────────────────
-- VIEW: Island Statistics by County
-- ────────────────────────────────────────────────────────────────────────────
CREATE VIEW IF NOT EXISTS geo_islands_by_county AS
SELECT 
    gc.id as county_id,
    gc.name as county_name,
    gc.lat as county_lat,
    gc.lng as county_lng,
    COUNT(gi.id) as island_count,
    GROUP_CONCAT(gi.name, ', ') as island_names
FROM geo_counties gc
LEFT JOIN geo_islands gi ON gc.id = gi.county_id
GROUP BY gc.id, gc.name, gc.lat, gc.lng;
