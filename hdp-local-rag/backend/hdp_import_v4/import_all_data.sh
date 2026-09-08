#!/bin/bash

# ============================================================
# 📥 اسکریپت کامل وارد کردن CSV به hdp_knowledge.db
# ============================================================

DB_PATH="/data/data/com.termux/files/home/hermezgan-intelligent/backend/hdp_import_v4/hdp_knowledge.db"
SOURCE_DIR="/data/data/com.termux/files/home/hermezgan-intelligent/backend/hdp_import_v4"

echo "=========================================="
echo "📥 شروع وارد کردن فایل‌های CSV"
echo "=========================================="

# 1. بیمارستان‌ها
echo "🏥 1. وارد کردن بیمارستان‌ها..."
sqlite3 "$DB_PATH" <<EOSQL
CREATE TABLE IF NOT EXISTS hospitals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    type TEXT,
    district TEXT,
    feature TEXT,
    bed_status TEXT
);
DELETE FROM hospitals;
.mode csv
.import "$SOURCE_DIR/05_hospitals.csv" hospitals
EOSQL
echo "✅ بیمارستان‌ها: $(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM hospitals;") رکورد"

# 2. مراکز خرید
echo "🛍️ 2. وارد کردن مراکز خرید..."
sqlite3 "$DB_PATH" <<EOSQL
CREATE TABLE IF NOT EXISTS shopping_centers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    type TEXT,
    location TEXT,
    size TEXT,
    hours TEXT,
    feature TEXT
);
DELETE FROM shopping_centers;
.mode csv
.import "$SOURCE_DIR/06_shopping.csv" shopping_centers
EOSQL
echo "✅ مراکز خرید: $(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM shopping_centers;") رکورد"

# 3. پارک‌ها
echo "🌳 3. وارد کردن پارک‌ها..."
sqlite3 "$DB_PATH" <<EOSQL
CREATE TABLE IF NOT EXISTS parks_recreation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    type TEXT,
    location TEXT,
    feature TEXT
);
DELETE FROM parks_recreation;
.mode csv
.import "$SOURCE_DIR/07_parks_recreation.csv" parks_recreation
EOSQL
echo "✅ پارک‌ها: $(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM parks_recreation;") رکورد"

# 4. دانشگاه‌ها
echo "🎓 4. وارد کردن دانشگاه‌ها..."
sqlite3 "$DB_PATH" <<EOSQL
CREATE TABLE IF NOT EXISTS universities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    type TEXT,
    location TEXT,
    majors TEXT,
    students TEXT
);
DELETE FROM universities;
.mode csv
.import "$SOURCE_DIR/08_universities.csv" universities
EOSQL
echo "✅ دانشگاه‌ها: $(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM universities;") رکورد"

# 5. صنایع
echo "🏭 5. وارد کردن صنایع..."
sqlite3 "$DB_PATH" <<EOSQL
CREATE TABLE IF NOT EXISTS industries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    activity TEXT,
    location TEXT,
    employees TEXT
);
DELETE FROM industries;
.mode csv
.import "$SOURCE_DIR/09_industries.csv" industries
EOSQL
echo "✅ صنایع: $(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM industries;") رکورد"

# 6. حمل و نقل
echo "🚌 6. وارد کردن حمل و نقل..."
sqlite3 "$DB_PATH" <<EOSQL
CREATE TABLE IF NOT EXISTS transport (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT,
    spec TEXT,
    status TEXT
);
DELETE FROM transport;
.mode csv
.import "$SOURCE_DIR/10_transport.csv" transport
EOSQL
echo "✅ حمل و نقل: $(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM transport;") رکورد"

# 7. اماکن مذهبی
echo "🕌 7. وارد کردن اماکن مذهبی..."
sqlite3 "$DB_PATH" <<EOSQL
CREATE TABLE IF NOT EXISTS religious_sites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    type TEXT,
    location TEXT,
    feature TEXT
);
DELETE FROM religious_sites;
.mode csv
.import "$SOURCE_DIR/11_religious.csv" religious_sites
EOSQL
echo "✅ اماکن مذهبی: $(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM religious_sites;") رکورد"

# 8. ادارات دولتی
echo "🏛️ 8. وارد کردن ادارات دولتی..."
sqlite3 "$DB_PATH" <<EOSQL
CREATE TABLE IF NOT EXISTS government_offices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    service TEXT,
    location TEXT
);
DELETE FROM government_offices;
.mode csv
.import "$SOURCE_DIR/12_government.csv" government_offices
EOSQL
echo "✅ ادارات: $(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM government_offices;") رکورد"

# 9. هتل‌ها
echo "🏨 9. وارد کردن هتل‌ها..."
sqlite3 "$DB_PATH" <<EOSQL
CREATE TABLE IF NOT EXISTS hotels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    grade TEXT,
    location TEXT,
    feature TEXT
);
DELETE FROM hotels;
.mode csv
.import "$SOURCE_DIR/13_hotels.csv" hotels
EOSQL
echo "✅ هتل‌ها: $(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM hotels;") رکورد"

# 10. آمار حاشیه‌نشینی
echo "📊 10. وارد کردن آمار حاشیه‌نشینی..."
sqlite3 "$DB_PATH" <<EOSQL
CREATE TABLE IF NOT EXISTS informal_settlements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    indicator TEXT,
    value TEXT,
    description TEXT
);
DELETE FROM informal_settlements;
.mode csv
.import "$SOURCE_DIR/14_informal_settlements.csv" informal_settlements
EOSQL
echo "✅ آمار حاشیه‌نشینی: $(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM informal_settlements;") رکورد"

# 11. مختصات GIS
echo "🗺️ 11. وارد کردن مختصات GIS..."
sqlite3 "$DB_PATH" <<EOSQL
CREATE TABLE IF NOT EXISTS gis_coordinates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    latitude REAL,
    longitude REAL,
    type TEXT
);
DELETE FROM gis_coordinates;
.mode csv
.import "$SOURCE_DIR/15_gis_coordinates.csv" gis_coordinates
EOSQL
echo "✅ مختصات: $(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM gis_coordinates;") رکورد"

# 12. اطلاعات جامع شهر
echo "📋 12. وارد کردن اطلاعات جامع شهر..."
sqlite3 "$DB_PATH" <<EOSQL
CREATE TABLE IF NOT EXISTS city_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    indicator TEXT,
    value TEXT
);
DELETE FROM city_info;
.mode csv
.import "$SOURCE_DIR/comprehensive_info_bandarabbas.csv" city_info
EOSQL
echo "✅ اطلاعات جامع: $(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM city_info;") رکورد"

# 13. صنایع و اقتصاد
echo "💰 13. وارد کردن صنایع و اقتصاد..."
sqlite3 "$DB_PATH" <<EOSQL
CREATE TABLE IF NOT EXISTS economy_industry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    activity TEXT,
    location TEXT,
    employees TEXT,
    product TEXT
);
DELETE FROM economy_industry;
.mode csv
.import "$SOURCE_DIR/economy_industry_bandarabbas.csv" economy_industry
EOSQL
echo "✅ اقتصاد و صنعت: $(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM economy_industry;") رکورد"

# 14. آموزش
echo "📚 14. وارد کردن آموزش..."
sqlite3 "$DB_PATH" <<EOSQL
CREATE TABLE IF NOT EXISTS education (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    type TEXT,
    location TEXT,
    students TEXT
);
DELETE FROM education;
.mode csv
.import "$SOURCE_DIR/education_bandarabbas.csv" education
EOSQL
echo "✅ آموزش: $(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM education;") رکورد"

# 15. تاریخچه
echo "📜 15. وارد کردن تاریخچه..."
sqlite3 "$DB_PATH" <<EOSQL
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    period TEXT,
    year TEXT,
    event TEXT,
    population TEXT
);
DELETE FROM history;
.mode csv
.import "$SOURCE_DIR/history_bandarabbas.csv" history
EOSQL
echo "✅ تاریخچه: $(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM history;") رکورد"

# 16. محلات تفصیلی
echo "🏘️ 16. وارد کردن محلات تفصیلی..."
sqlite3 "$DB_PATH" <<EOSQL
CREATE TABLE IF NOT EXISTS neighborhoods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    old_name TEXT,
    zone TEXT,
    district TEXT,
    texture TEXT
);
DELETE FROM neighborhoods;
.mode csv
.import "$SOURCE_DIR/neighborhoods_detailed_bandarabbas.csv" neighborhoods
EOSQL
echo "✅ محلات: $(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM neighborhoods;") رکورد"

# 17. اسکله‌ها
echo "⚓ 17. وارد کردن اسکله‌ها..."
sqlite3 "$DB_PATH" <<EOSQL
CREATE TABLE IF NOT EXISTS piers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    type TEXT,
    location TEXT,
    distance_km TEXT,
    travel_time TEXT
);
DELETE FROM piers;
.mode csv
.import "$SOURCE_DIR/piers_navigation.csv" piers
EOSQL
echo "✅ اسکله‌ها: $(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM piers;") رکورد"

# 18. ورزش
echo "⚽ 18. وارد کردن مراکز ورزشی..."
sqlite3 "$DB_PATH" <<EOSQL
CREATE TABLE IF NOT EXISTS sports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    type TEXT,
    location TEXT,
    capacity TEXT
);
DELETE FROM sports;
.mode csv
.import "$SOURCE_DIR/sports_bandarabbas.csv" sports
EOSQL
echo "✅ ورزش: $(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM sports;") رکورد"

# 19. درمان
echo "💊 19. وارد کردن مراکز درمانی..."
sqlite3 "$DB_PATH" <<EOSQL
CREATE TABLE IF NOT EXISTS treatment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    type TEXT,
    zone TEXT,
    beds TEXT
);
DELETE FROM treatment;
.mode csv
.import "$SOURCE_DIR/treatment_bandarabbas.csv" treatment
EOSQL
echo "✅ درمان: $(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM treatment;") رکورد"

# 20. مناطق شهری
echo "🗺️ 20. وارد کردن مناطق شهری..."
sqlite3 "$DB_PATH" <<EOSQL
CREATE TABLE IF NOT EXISTS urban_zones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    zone TEXT,
    local_name TEXT,
    neighborhoods TEXT,
    population TEXT,
    feature TEXT,
    infrastructure TEXT
);
DELETE FROM urban_zones;
.mode csv
.import "$SOURCE_DIR/urban_zones_bandarabbas.csv" urban_zones
EOSQL
echo "✅ مناطق شهری: $(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM urban_zones;") رکورد"

# آمار نهایی
echo ""
echo "=========================================="
echo "📊 آمار نهایی وارد کردن داده‌ها"
echo "=========================================="

sqlite3 "$DB_PATH" <<EOSQL
SELECT '📋 لیست جداول و تعداد رکوردها:' as '';
SELECT '------------------------------' as '';
SELECT 'hospitals: ' || COUNT(*) FROM hospitals;
SELECT 'shopping_centers: ' || COUNT(*) FROM shopping_centers;
SELECT 'parks_recreation: ' || COUNT(*) FROM parks_recreation;
SELECT 'universities: ' || COUNT(*) FROM universities;
SELECT 'industries: ' || COUNT(*) FROM industries;
SELECT 'transport: ' || COUNT(*) FROM transport;
SELECT 'religious_sites: ' || COUNT(*) FROM religious_sites;
SELECT 'government_offices: ' || COUNT(*) FROM government_offices;
SELECT 'hotels: ' || COUNT(*) FROM hotels;
SELECT 'informal_settlements: ' || COUNT(*) FROM informal_settlements;
SELECT 'gis_coordinates: ' || COUNT(*) FROM gis_coordinates;
SELECT 'city_info: ' || COUNT(*) FROM city_info;
SELECT 'economy_industry: ' || COUNT(*) FROM economy_industry;
SELECT 'education: ' || COUNT(*) FROM education;
SELECT 'history: ' || COUNT(*) FROM history;
SELECT 'neighborhoods: ' || COUNT(*) FROM neighborhoods;
SELECT 'piers: ' || COUNT(*) FROM piers;
SELECT 'sports: ' || COUNT(*) FROM sports;
SELECT 'treatment: ' || COUNT(*) FROM treatment;
SELECT 'urban_zones: ' || COUNT(*) FROM urban_zones;
EOSQL

echo ""
echo "=========================================="
echo "✅ وارد کردن تمام فایل‌ها با موفقیت انجام شد!"
echo "=========================================="
