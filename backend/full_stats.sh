#!/bin/bash

echo "=========================================="
echo "📊 گزارش کامل آماری پایگاه داده"
echo "=========================================="

sqlite3 /data/data/com.termux/files/home/hermezgan-intelligent/backend/hdp_import_v4/hdp_knowledge.db <<'SQL'

-- ============================================================
-- 1. آمار کلی جداول
-- ============================================================
SELECT '📊 آمار کلی جداول' as '';
SELECT '==================' as '';
SELECT 
    'hospitals' as جدول,
    COUNT(*) as تعداد 
FROM hospitals
UNION ALL SELECT 'shopping_centers', COUNT(*) FROM shopping_centers
UNION ALL SELECT 'hotels', COUNT(*) FROM hotels
UNION ALL SELECT 'universities', COUNT(*) FROM universities
UNION ALL SELECT 'schools', COUNT(*) FROM schools
UNION ALL SELECT 'restaurants', COUNT(*) FROM restaurants
UNION ALL SELECT 'cafes', COUNT(*) FROM cafes
UNION ALL SELECT 'parks', COUNT(*) FROM parks
UNION ALL SELECT 'fuel_stations', COUNT(*) FROM fuel_stations
UNION ALL SELECT 'police_stations', COUNT(*) FROM police_stations
UNION ALL SELECT 'cameras', COUNT(*) FROM cameras
UNION ALL SELECT 'knowledge', COUNT(*) FROM knowledge
UNION ALL SELECT 'traffic_cameras', COUNT(*) FROM traffic_cameras
UNION ALL SELECT 'traffic_blackspots', COUNT(*) FROM traffic_blackspots
UNION ALL SELECT 'graph_nodes', COUNT(*) FROM graph_nodes
UNION ALL SELECT 'graph_edges', COUNT(*) FROM graph_edges
ORDER BY تعداد DESC;

-- ============================================================
-- 2. آمار تکراری‌ها
-- ============================================================
SELECT '' as '';
SELECT '🔍 آمار تکراری‌ها:' as '';
SELECT '=================' as '';

SELECT 'بیمارستان‌های تکراری:' as '';
SELECT name, COUNT(*) as تکرار FROM hospitals GROUP BY name HAVING COUNT(*) > 1;

SELECT 'رستوران‌های تکراری:' as '';
SELECT name, COUNT(*) as تکرار FROM restaurants GROUP BY name HAVING COUNT(*) > 1 LIMIT 10;

SELECT 'هتل‌های تکراری:' as '';
SELECT name, COUNT(*) as تکرار FROM hotels GROUP BY name HAVING COUNT(*) > 1 LIMIT 10;

-- ============================================================
-- 3. آمار دسته‌بندی شده
-- ============================================================
SELECT '' as '';
SELECT '📈 آمار دسته‌بندی شده:' as '';
SELECT '=====================' as '';

SELECT 'بیمارستان‌ها بر اساس نوع:' as '';
SELECT type, COUNT(*) as تعداد FROM hospitals GROUP BY type;

SELECT 'رستوران‌ها بر اساس نوع:' as '';
SELECT type, COUNT(*) as تعداد FROM restaurants GROUP BY type ORDER BY COUNT(*) DESC LIMIT 5;

SELECT 'هتل‌ها بر اساس درجه:' as '';
SELECT grade, COUNT(*) as تعداد FROM hotels GROUP BY grade;

SELECT 'دوربین‌ها بر اساس وضعیت:' as '';
SELECT status, COUNT(*) as تعداد FROM cameras GROUP BY status;

SELECT 'جایگاه‌های سوخت بر اساس نوع:' as '';
SELECT type, COUNT(*) as تعداد FROM fuel_stations GROUP BY type;

-- ============================================================
-- 4. جمع کل
-- ============================================================
SELECT '' as '';
SELECT '📊 جمع کل:' as '';
SELECT '=========' as '';
SELECT 'مجموع کل رکوردها: ' || (
    (SELECT COUNT(*) FROM hospitals) +
    (SELECT COUNT(*) FROM shopping_centers) +
    (SELECT COUNT(*) FROM hotels) +
    (SELECT COUNT(*) FROM universities) +
    (SELECT COUNT(*) FROM schools) +
    (SELECT COUNT(*) FROM restaurants) +
    (SELECT COUNT(*) FROM cafes) +
    (SELECT COUNT(*) FROM parks) +
    (SELECT COUNT(*) FROM fuel_stations) +
    (SELECT COUNT(*) FROM police_stations) +
    (SELECT COUNT(*) FROM cameras) +
    (SELECT COUNT(*) FROM knowledge) +
    (SELECT COUNT(*) FROM traffic_cameras) +
    (SELECT COUNT(*) FROM traffic_blackspots) +
    (SELECT COUNT(*) FROM graph_nodes) +
    (SELECT COUNT(*) FROM graph_edges)
) || ' رکورد' as مجموع;

SQL

echo ""
echo "=========================================="
echo "✅ گزارش کامل آماری با موفقیت نمایش داده شد!"
echo "=========================================="
