# راهنمای GEO.DB - پایگاه داده جغرافیایی هرمزگان

## 📍 مقدمه

`geo.db` یک پایگاه داده SQLite است که برای ذخیره و جستجوی داده‌های جغرافیایی استفاده می‌شود. این پایگاه داده شامل:

- **داده‌های مکانی**: استفاده از R-Tree برای جستجوی سریع و کارآمد
- **جغرافیای اداری**: شهرستان‌ها و جزایر استان هرمزگان
- **POIs**: نقاط مورد علاقه (درمانگاه، پمپ بنزین، دوربین‌های ترافیکی، و غیره)
- **ترافیک زنده**: داده‌های ترافیک به‌روز شده

## 🛠️ نصب و راه‌اندازی

### 1. پیش‌نیازها

```bash
# نصب Python 3.7+
python3 --version

# نصب sqlite3 (معمولاً پیش‌فرض است)
sqlite3 --version
```

### 2. مقداردهی اولیه پایگاه داده

```bash
# اجرای script مقداردهی اولیه
python3 init_geodb.py

# یا با مسیرهای سفارشی
python3 init_geodb.py --db data/geo.db --force
```

**خروجی انتظار‌رفته:**
```
🗄️  GEO.DB INITIALIZATION
============================================================

1️⃣  Connecting to database...
✓ Database connected with WAL mode enabled

2️⃣  Applying base spatial schema...
✓ Applied database/schema.sql - Spatial R-Tree indexing

3️⃣  Applying administrative geography schema...
✓ Applied database/schema_admin_geo.sql - Counties and Islands

4️⃣  Verifying database structure...
============================================================
TABLE VERIFICATION
============================================================
✓ pois                       (    13 rows)
✓ traffic                    (     0 rows)
✓ cameras                    (     0 rows)
✓ hospitals                  (     0 rows)
✓ fuel_stations              (     0 rows)
✓ roads                      (     0 rows)
✓ geo_counties               (    13 rows)
✓ geo_islands                (    14 rows)
============================================================

5️⃣  Generating statistics...
```

### 3. وارد کردن داده‌های فهرست هرمزگان

```bash
# وارد کردن داده‌های شهرستان‌ها و جزایر
python3 import_hormozgan_atlas.py \
  --db geo.db \
  --atlas hormozgan_atlas_dictionary.json
```

## 📊 ساختار پایگاه داده

### جداول اصلی

#### `geo_counties` - شهرستان‌ها
```
┌─────────────────────────────────────────────────┐
│ id (PRIMARY KEY)                                │
│ name (متن فارسی - UNIQUE)                      │
│ center (شهر مرکزی)                             │
│ lat, lng (مختصات)                              │
│ aliases_json (نام‌های جایگزین)                 │
│ description (توضیحات)                          │
│ updated_at (زمان آپدیت)                        │
└─────────────────────────────────────────────────┘
```

**مثال:**
```json
{
  "id": 1,
  "name": "بندرعباس",
  "center": "بندرعباس",
  "lat": 27.1842,
  "lng": 56.2893,
  "aliases_json": ["Bandar Abbas", "Bندر عباس"]
}
```

#### `geo_islands` - جزایر
```
┌─────────────────────────────────────────────────┐
│ id (PRIMARY KEY)                                │
│ name (متن فارسی - UNIQUE)                      │
│ county_id (FOREIGN KEY → geo_counties)          │
│ lat, lng (مختصات)                              │
│ aliases_json (نام‌های جایگزین)                 │
│ type (نوع: island)                             │
│ description (توضیحات)                          │
│ updated_at (زمان آپدیت)                        │
└─────────────────────────────────────────────────┘
```

**مثال:**
```json
{
  "id": 1,
  "name": "قشم",
  "county_id": 3,
  "lat": 26.8264,
  "lng": 55.9355,
  "aliases_json": ["Qeshm"],
  "type": "island"
}
```

#### `pois` - نقاط مورد علاقه
```
┌─────────────────────────────────────────────────┐
│ id (PRIMARY KEY)                                │
│ category (دسته‌بندی)                           │
│ name (نام)                                     │
│ lat, lng (مختصات)                              │
│ description (توضیحات)                          │
│ tags_json (برچسب‌های اضافی)                    │
│ tenant_uuid (نشانگر چند‌مؤسسه)                  │
│ updated_at (زمان آپدیت)                        │
└─────────────────────────────────────────────────┘
```

#### `traffic` - داده‌های ترافیک زنده
```
┌─────────────────────────────────────────────────┐
│ id (PRIMARY KEY)                                │
│ name (نام مقطع راه)                            │
│ lat, lng (مختصات)                              │
│ level (سطح ترافیک: light/medium/heavy)         │
│ speed_kmh (سرعت متوسط)                         │
│ delay_min (تأخیر بر حسب دقیقه)                 │
│ updated_at (زمان آپدیت)                        │
└─────────────────────────────────────────────────┘
```

#### `cameras` - دوربین‌های ترافیکی
```
┌─────────────────────────────────────────────────┐
│ id (PRIMARY KEY)                                │
│ code (کد انسانی: ba-001)                        │
│ name (نام)                                     │
│ lat, lng (مختصات)                              │
│ status (وضعیت: active/installing/pending)      │
│ types_json (نوع‌ها: speed, plate, etc)         │
│ updated_at (زمان آپدیت)                        │
└─────────────────────────────────────────────────┘
```

### جدول‌های کمکی (R-Tree)

هر جدول مکانی دارای یک جدول R-Tree مطابقت‌دهنده است:
- `geo_counties_rtree`
- `geo_islands_rtree`
- `pois_rtree`
- `traffic_rtree`
- `cameras_rtree`
- `hospitals_rtree`
- `fuel_stations_rtree`
- `roads_rtree`

### ویوها (Views)

#### `geo_all_points` - تمام نقاط جغرافیایی
```sql
SELECT * FROM geo_all_points;
-- برمی‌گرداند: شهرستان‌ها و جزایر در یک جدول
```

#### `geo_islands_by_county` - جزایر بر اساس شهرستان
```sql
SELECT * FROM geo_islands_by_county;
-- برمی‌گرداند: تعداد جزایر هر شهرستان
```

## 🔍 نمونه‌های استعلام

### 1. دریافت تمام شهرستان‌ها
```sql
SELECT id, name, lat, lng, center 
FROM geo_counties 
ORDER BY name;
```

**نتیجه:**
```
id | name       | lat     | lng     | center
-- | ---------- | ------- | ------- | ----------
1  | بندرعباس | 27.1842 | 56.2893 | بندرعباس
2  | میناب      | 27.1506 | 57.0753 | میناب
3  | قشم       | 26.7833 | 55.8667 | قشم
...
```

### 2. دریافت جزایر یک شهرستان
```sql
SELECT gi.name, gi.lat, gi.lng
FROM geo_islands gi
JOIN geo_counties gc ON gi.county_id = gc.id
WHERE gc.name = 'قشم'
ORDER BY gi.name;
```

**نتیجه:**
```
name    | lat     | lng
------- | ------- | -------
قشم    | 26.8264 | 55.9355
هرمز   | 27.0649 | 56.4644
هنگام   | 26.6485 | 55.8794
لارک   | 26.8558 | 56.364
```

### 3. جستجوی نقاط در یک مربع محدود (Bounding Box)
```sql
SELECT * FROM pois
WHERE lat BETWEEN 26.5 AND 27.5 AND lng BETWEEN 55 AND 57
ORDER BY name;
```

### 4. جستجوی سریع با R-Tree
```sql
SELECT p.* FROM pois p
JOIN pois_rtree pr ON p.id = pr.id
WHERE pr.min_lat BETWEEN 26.5 AND 27.5 
  AND pr.min_lng BETWEEN 55 AND 57
ORDER BY p.name;
```

### 5. شمار جزایر بر حسب شهرستان
```sql
SELECT gc.name as county, COUNT(gi.id) as island_count
FROM geo_counties gc
LEFT JOIN geo_islands gi ON gc.id = gi.county_id
GROUP BY gc.id, gc.name
ORDER BY island_count DESC;
```

**نتیجه:**
```
county     | island_count
---------- | -----
ابوموسی   | 6
قشم       | 4
بندرلنگه  | 4
(سایر شهرستان‌ها) | 0
```

### 6. جستجو با نام جایگزین (Alias)
```sql
SELECT * FROM geo_counties 
WHERE aliases_json LIKE '%Bandar Abbas%'
   OR name = 'بندرعباس';
```

## 🚀 بهترین روش‌ها

### 1. استفاده از R-Tree برای عملکرد بهتر
```python
# نیاکم: SELECT * FROM pois WHERE ...
# بهتر: استفاده از R-Tree برای پیش‌فیلتر

import sqlite3

conn = sqlite3.connect('geo.db')
cursor = conn.cursor()

# جستجوی سریع در R-Tree
cursor.execute('''
    SELECT p.* FROM pois p
    JOIN pois_rtree pr ON p.id = pr.id
    WHERE pr.min_lat BETWEEN ? AND ? 
      AND pr.min_lng BETWEEN ? AND ?
''', (26.5, 27.5, 55, 57))

results = cursor.fetchall()
```

### 2. استفاده از Index‌ها
```sql
-- جستجو بر اساس دسته (indexed)
SELECT * FROM pois WHERE category = 'administrative/county';

-- جستجو بر اساس نام (indexed)
SELECT * FROM geo_counties WHERE name = 'بندرعباس';
```

### 3. Transaction برای عملیات گروهی
```python
cursor = conn.cursor()
try:
    cursor.execute("BEGIN TRANSACTION")
    
    for county in counties:
        cursor.execute('''
            INSERT INTO geo_counties (name, lat, lng) 
            VALUES (?, ?, ?)
        ''', (county['name'], county['lat'], county['lng']))
    
    conn.commit()
except Exception as e:
    conn.rollback()
    raise e
```

### 4. استفاده از JSON برای داده‌های متغیر
```python
import json

aliases = ["Bandar Abbas", "Bندر عباس"]
tags = {"region": "south", "coastal": True}

cursor.execute('''
    UPDATE geo_counties 
    SET aliases_json = ?, 
        description = ?
    WHERE id = ?
''', (json.dumps(aliases), json.dumps(tags), 1))
```

## 📈 بهینه‌سازی

### فعال‌سازی WAL Mode
```sql
PRAGMA journal_mode = WAL;
```
- بهتر برای همزمانی (concurrency)
- سرعت نوشتن بیشتر
- شناور خودکار

### فعال‌سازی Foreign Keys
```sql
PRAGMA foreign_keys = ON;
```
- تضمین یکپارچگی داده‌ها
- جلوگیری از داده‌های یتیم

### بزرگ‌نمایی Cache
```sql
PRAGMA cache_size = 10000;  -- 10000 صفحات
```

## 🔧 ابزارهای مدیریت

### نسخه‌پیشی (Backup)
```bash
sqlite3 geo.db ".backup geo_backup.db"
```

### بررسی تمامیت
```bash
sqlite3 geo.db "PRAGMA integrity_check;"
```

### بهینه‌سازی
```bash
sqlite3 geo.db "VACUUM;"
```

### آمار توالی‌های استعلام
```bash
sqlite3 geo.db "PRAGMA query_only = ON;"
sqlite3 geo.db "ANALYZE;"
```

## 📝 فهرست شهرستان‌ها و جزایر

### 13 شهرستان هرمزگان
1. 🏙️ بندرعباس (Bandar Abbas)
2. 🌾 میناب (Minab)
3. 🏝️ قشم (Qeshm)
4. 🚢 بندرلنگه (Bandar Lengeh)
5. 📍 پارسیان (Parsian)
6. 🏞️ حاجی‌آباد (Hajiabad)
7. 🌊 رودان (Rudan)
8. ⛰️ بشاگرد (Bashagard)
9. 🏖️ سیریک (Sirik)
10. 🎯 جاسک (Jask)
11. ⚓ خمیر (Khamir)
12. 🗺️ بستک (Bastak)
13. 🛣️ ابوموسی (Abu Musa)

### 14 جزیره اصلی
**در شهرستان قشم:**
- قشم، هرمز، هنگام، لارک

**در شهرستان بندرلنگه:**
- کیش، لاوان، هندورابی، شیدور

**در شهرستان ابوموسی:**
- ابوموسی، تنب بزرگ، تنب کوچک، سیری، فارور، فارور کوچک

## 🐛 عیب‌یابی

### خطا: "Table already exists"
```bash
# اجبار بازنشانی
python3 init_geodb.py --force
```

### خطا: "database is locked"
```bash
# حذف فایل‌های WAL
rm geo.db-wal geo.db-shm
```

### پرس‌وجو کند است
```sql
-- بررسی plan استعلام
EXPLAIN QUERY PLAN SELECT ...;

-- بازسازی Index‌ها
REINDEX;
```

## 📚 منابع بیشتر

- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [SQLite R-Tree Module](https://www.sqlite.org/rtree.html)
- [Haversine Formula](https://en.wikipedia.org/wiki/Haversine_formula)

## 📞 تماس و پشتیبانی

برای مسائل و پیشنهادات:
- GitHub Issues: https://github.com/hdpbnd/hermezgan-intelligent/issues
- Email: hormozgamahdi@gmail.com
