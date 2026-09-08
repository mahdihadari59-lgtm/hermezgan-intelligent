PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;

-------------------------------------------------
-- Roads
-------------------------------------------------

INSERT OR IGNORE INTO roads (
    id,
    name,
    min_lat,
    max_lat,
    min_lng,
    max_lng,
    road_class
)
SELECT
    id,
    name,
    lat,
    lat,
    lng,
    lng,
    category
FROM pois
WHERE category IN (
    'street',
    'residential_street',
    'boulevard',
    'alley'
);

-------------------------------------------------
-- Cameras
-------------------------------------------------

INSERT OR IGNORE INTO cameras (
    id,
    code,
    name,
    lat,
    lng,
    status,
    types_json
)
SELECT
    id,
    printf('cam-%06d',id),
    name,
    lat,
    lng,
    'active',
    json_array('speed')
FROM pois
WHERE category='speed_camera';

-------------------------------------------------
-- Traffic Signals
-------------------------------------------------

INSERT OR IGNORE INTO traffic (
    id,
    name,
    lat,
    lng,
    level,
    speed_kmh,
    delay_min
)
SELECT
    id,
    name,
    lat,
    lng,
    'light',
    NULL,
    NULL
FROM pois
WHERE category='traffic_signal';

COMMIT;
