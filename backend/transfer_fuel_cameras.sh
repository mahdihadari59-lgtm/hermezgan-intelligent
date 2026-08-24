#!/bin/bash

echo "=========================================="
echo "⛽ انتقال داده‌های جایگاه‌های سوخت و دوربین‌ها"
echo "=========================================="

sqlite3 /data/data/com.termux/files/home/hermezgan-intelligent/backend/hdp_import_v4/hdp_knowledge.db <<'SQL'

-- ============================================================
-- 1. اتصال به geo.db
-- ============================================================
ATTACH DATABASE '/data/data/com.termux/files/home/hermezgan-intelligent-backup-20260729/database/geo.db' AS geo;

-- ============================================================
-- 2. بررسی تعداد داده‌ها در geo.db
-- ============================================================
SELECT '📊 تعداد fuel_stations در geo.db: ' || COUNT(*) FROM geo.fuel_stations;
SELECT '📊 تعداد cameras در geo.db: ' || COUNT(*) FROM geo.cameras;

-- ============================================================
-- 3. انتقال جایگاه‌های سوخت
-- ============================================================
INSERT OR IGNORE INTO fuel_stations (name, type, location, lat, lng, address)
SELECT 
    name,
    CASE 
        WHEN gasoline = 1 AND cng = 1 AND diesel = 1 THEN 'بنزین - CNG - گازوئیل'
        WHEN gasoline = 1 AND cng = 1 THEN 'بنزین - CNG'
        WHEN gasoline = 1 AND diesel = 1 THEN 'بنزین - گازوئیل'
        WHEN gasoline = 1 THEN 'بنزین'
        WHEN cng = 1 THEN 'CNG'
        WHEN diesel = 1 THEN 'گازوئیل'
        ELSE 'نامشخص'
    END,
    hours,
    lat,
    lng,
    'از geo.db'
FROM geo.fuel_stations
WHERE lat IS NOT NULL AND lng IS NOT NULL;

-- ============================================================
-- 4. انتقال دوربین‌ها
-- ============================================================
INSERT OR IGNORE INTO cameras (name, type, location, lat, lng, status, address)
SELECT 
    name,
    types_json,
    'از geo.db',
    lat,
    lng,
    status,
    code
FROM geo.cameras
WHERE lat IS NOT NULL AND lng IS NOT NULL;

-- ============================================================
-- 5. جدا کردن
-- ============================================================
DETACH DATABASE geo;

-- ============================================================
-- 6. نمایش آمار نهایی
-- ============================================================
SELECT '📊 آمار نهایی پس از انتقال' as '';
SELECT '--------------------------' as '';
SELECT 'fuel_stations: ' || COUNT(*) FROM fuel_stations;
SELECT 'cameras: ' || COUNT(*) FROM cameras;

-- ============================================================
-- 7. نمایش نمونه داده‌ها
-- ============================================================
SELECT '📋 نمونه fuel_stations:' as '';
SELECT name, type, lat, lng FROM fuel_stations LIMIT 5;

SELECT '📋 نمونه cameras:' as '';
SELECT name, type, status, lat, lng FROM cameras LIMIT 5;

SQL

echo ""
echo "=========================================="
echo "✅ انتقال داده‌ها با موفقیت انجام شد!"
echo "=========================================="
