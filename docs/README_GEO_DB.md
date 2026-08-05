# 🗄️ GEO.DB - سیستم پایگاه داده جغرافیایی بندرعباس

**سیستم جامع مدیریت و جستجوی داده‌های جغرافیایی شهر بندرعباس و استان هرمزگان**

[![Python 3.7+](https://img.shields.io/badge/Python-3.7%2B-blue)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/Database-SQLite-green)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 📊 خصوصیات اصلی

### 📍 داده‌های جغرافیایی
- **677 مکان** در شهر بندرعباس (رستوران، کافه، هتل، بیمارستان، و غیره)
- **13 شهرستان** در استان هرمزگان
- **14 جزیره** اصلی در خلیج فارس
- **R-Tree Spatial Indexing** برای جستجوی سریع و کارآمد

### 🚀 عملکرد
- **جستجو در کمتر از ۱ms** (با استفاده از R-Tree)
- **دسترسی همزمان** (WAL Mode فعال)
- **یکپارچگی داده‌ها** (Foreign Keys)

### 💻 رابط برنامه‌نویسی
- **Python API** برای دسترسی آسان
- **SQL Query** برای سؤال‌های پیچیده
- **Knowledge Base** برای جستجوی متون
- **Search Index** برای جستجوی سریع

---

## 🛠️ نصب و راه‌اندازی

### الزامات
```bash
# Python 3.7 یا بالاتر
python3 --version

# SQLite (معمولاً پیش‌فرض است)
sqlite3 --version
```

### نصب سریع (یک‌دستور)

```bash
# تمام مراحل راه‌اندازی به صورت خودکار
python3 setup_geodb.py
```

### نصب مرحله‌ای

```bash
# مرحله ۱: مقداردهی اولیه پایگاه داده
python3 init_geodb.py

# مرحله ۲: وارد کردن داده‌های هرمزگان
python3 import_hormozgan_atlas.py \
  --db geo.db \
  --atlas hormozgan_atlas_dictionary.json

# مرحله ۳: وارد کردن 677 مکان بندرعباس
python3 import_bandar_places.py \
  --db geo.db \
  --places bandar_places.json

# مرحله ۴: ایجاد دانشنامه و شاخص جستجو
python3 generate_places_kb.py --db geo.db
```

---

## 📚 نمونه‌های استفاده

### ۱️⃣ جستجو در مک��ن‌ها (Python)

```python
from geodb import Places

# جستجو بر اساس نام
with Places() as places:
    cafes = places.search_by_name("کافه")
    print(f"یافت شد: {len(cafes)} کافه")
    
    for cafe in cafes[:5]:
        print(f"  • {cafe['name']} ({cafe['lat']}, {cafe['lng']})")
```

### ۲️⃣ جستجوی مکانی (Spatial Query)

```python
from geodb import Places

# یافتن تمام رستوران‌ها در شعاع ۳ کیلومتری
with Places() as places:
    # مختصات مرکز بندرعباس: 27.1842, 56.2893
    restaurants = places.get_by_location(
        lat=27.1842, 
        lng=56.2893, 
        radius_km=3.0
    )
    
    for r in restaurants:
        print(f"{r['icon']} {r['name']}")
        print(f"   فاصله: {r['distance_km']:.2f} کیلومتر\n")
```

### ۳️⃣ دسته‌بندی‌ها (Categories)

```python
from geodb import Places

with Places() as places:
    # تمام دسته‌ها
    categories = places.get_categories()
    
    for cat in categories:
        print(f"{cat['icon']} {cat['category_name']}: {cat['count']} مورد")
```

### ۴️⃣ جزایر شهرستان‌ها (Islands)

```python
from geodb import Islands

with Islands() as islands:
    # جزایر قشم
    qeshm_islands = islands.get_by_county("قشم")
    
    print(f"جزایر قشم ({len(qeshm_islands)}):")
    for island in qeshm_islands:
        print(f"  • {island['name']}")
```

### ۵️⃣ آمار و تحلیل (Analytics)

```python
from geodb import Analytics

with Analytics() as analytics:
    overview = analytics.get_overview()
    
    print("📊 خلاصه پایگاه داده:")
    for table, count in overview.items():
        print(f"  {table}: {count}")
```

---

## 🔍 نمونه‌های SQL

### تمام رستوران‌های بندرعباس

```sql
SELECT name, category_name, lat, lng, icon
FROM places
WHERE category = 'restaurant'
ORDER BY name;
```

### مکان‌های در منطقه‌ای خاص

```sql
SELECT * FROM places
WHERE lat BETWEEN 27.1 AND 27.3
  AND lng BETWEEN 56.2 AND 56.5
ORDER BY name;
```

### جستجوی سریع با R-Tree

```sql
SELECT p.* FROM places p
JOIN places_rtree pr ON p.id = pr.id
WHERE pr.min_lat BETWEEN 27.0 AND 27.3
  AND pr.min_lng BETWEEN 56.0 AND 56.5;
```

### آمار مکان‌ها بر حسب دسته

```sql
SELECT 
  category_name, 
  COUNT(*) as count,
  icon
FROM places
GROUP BY category_name
ORDER BY count DESC;
```

### جزایر و شهرستان‌های آن‌ها

```sql
SELECT 
  gi.name as island, 
  gc.name as county,
  gi.lat, 
  gi.lng
FROM geo_islands gi
JOIN geo_counties gc ON gi.county_id = gc.id
ORDER BY gc.name, gi.name;
```

---

## 📊 ساختار داده‌ها

### جدول `places` - مکان‌های بندرعباس

```
┌─────────────────────────────────────────────────┐
│ ID (INTEGER PRIMARY KEY)                        │
│ name (TEXT) - نام مکان                         │
│ category (TEXT) - دسته (cafe, restaurant, ...) │
│ category_name (TEXT) - نام فارسی دسته         │
│ lat, lng (REAL) - مختصات GPS                   │
│ description (TEXT) - توضیحات                   │
│ icon (TEXT) - نماد emoji                       │
│ tags_json (TEXT) - برچسب‌های JSON             │
│ updated_at (INTEGER) - زمان آپدیت              │
└─────────────────────────────────────────────────┘
```

### جدول `geo_counties` - شهرستان‌ها

```
┌─────────────────────────────────────────────────┐
│ ID (INTEGER PRIMARY KEY)                        │
│ name (TEXT UNIQUE) - نام شهرستان               │
│ center (TEXT) - شهر مرکزی                      │
│ lat, lng (REAL) - مختصات مرکزی                 │
│ aliases_json (TEXT) - نام‌های جایگزین         │
│ updated_at (INTEGER) - زمان آپدیت              │
└─────────────────────────────────────────────────┘
```

### جدول `geo_islands` - جزایر

```
┌─────────────────────────────────────────────────┐
│ ID (INTEGER PRIMARY KEY)                        │
│ name (TEXT UNIQUE) - نام جزیره                 │
│ county_id (FK) - شهرستان مربوط                │
│ lat, lng (REAL) - مختصات                      │
│ aliases_json (TEXT) - نام‌های جایگزین         │
│ updated_at (INTEGER) - زمان آپدیت              │
└─────────────────────────────────────────────────┘
```

---

## 📁 ساختار فایل‌ها

```
hermezgan-intelligent/
├── database/
│   ├── schema.sql                    # اسکیمای اصلی
│   └── schema_admin_geo.sql          # اسکیمای جغرافیایی
│
├── setup_geodb.py                    # اسکریپت راه‌اندازی کامل
├── init_geodb.py                     # مقداردهی اولیه
├── import_hormozgan_atlas.py         # وارد‌کردن اطلاعات هرمزگان
├── import_bandar_places.py           # وارد‌کردن 677 مکان
├── generate_places_kb.py             # ایجاد دانشنامه
│
├── geodb.py                          # ماژول Python
│
├── hormozgan_atlas_dictionary.json   # داده‌های جغرافیایی
├── bandar_places.json                # داده‌های 677 مکان
│
├── docs/
│   ├── GEO_DB_GUIDE.md               # راهنمای جامع
│   └── QUICK_START.md                # راهنمای سریع
│
├── geo.db                            # پایگاه داده (تولید شده)
├── bandar_places_knowledge.json      # دانشنامه (تولید شده)
└── bandar_places_search_index.json   # شاخص جستجو (تولید شده)
```

---

## 🎯 دسته‌های مکان

| کد | نام | نماد | توضیح |
|----|-----|------|-------|
| cafe | کافه‌ها | ☕ | کافه‌ها و چایخانه‌ها |
| restaurant | رستوران‌ها | 🍽️ | رستوران‌های مختلف |
| hotel | هتل‌ها | 🏨 | اقامتگاه‌های مختلف |
| hospital | بیمارستان‌ها | 🏥 | بیمارستان‌ها و کلینیک‌ها |
| pharmacy | داروخانه‌ها | 💊 | داروخانه‌های شبانه‌روزی |
| bank | بانک‌ها | 🏦 | بانک‌ها و نمایندگی‌ها |
| fuel | پمپ بنزین | ⛽ | جایگاه‌های سوخت |
| school | مدارس | 🏫 | مدارس و دانشگاه‌ها |
| police | پلیس | 👮 | کلانتری‌ها و پاسگاه‌ها |
| park | پارک‌ها | 🌳 | پارک‌های شهری |
| market | بازارها | 🛍️ | بازارها و مراکز خرید |
| mosque | مساجد | 🕌 | مساجد و امامزاده‌ها |
| parking | پارکینگ‌ها | 🅿️ | پارکینگ‌های عمومی |
| bus_station | پایانه‌ها | 🚌 | ایستگاه‌های اتوبوس |
| atm | خودپردازها | 💰 | دستگاه‌های خودپرداز |

---

## 🌍 جغرافیای هرمزگان

### ۱۳ شهرستان
بندرعباس • میناب • قشم • بندرلنگه • پارسیان • حاجی‌آباد • رودان • بشاگرد • سیریک • جاسک • خمیر • بستک • ابوموسی

### ۱۴ جزیره اصلی
**قشم:** قشم • هرمز • هنگام • لارک
**بندرلنگه:** کیش • لاوان • هندورابی • شیدور
**ابوموسی:** ابوموسی • تنب بزرگ • تنب کوچک • سیری • فارور • فارور کوچک

---

## ⚡ نکات عملکرد

### R-Tree Spatial Indexing
- جستجوهای مکانی در **< 1ms**
- استفاده برای جستجوی سریع در مربع‌های محدود
- فیلترینگ دقیق با فرمول Haversine

### WAL Mode
- حمایت از دسترسی‌های **همزمان**
- نوشتن سریع‌تر
- شناور خودکار

### Foreign Keys
- تضمین **یکپارچگی داده‌ها**
- جلوگیری از داده‌های یتیم
- حذف CASCADE برای روابط

---

## 📖 مستندات

- 📘 [GEO_DB_GUIDE.md](docs/GEO_DB_GUIDE.md) - راهنمای جامع
- 📗 [QUICK_START.md](docs/QUICK_START.md) - راهنمای سریع

---

## 🔧 عیب‌یابی

### مشکل: "Table already exists"
```bash
python3 setup_geodb.py  # بازنشانی کامل
```

### مشکل: "database is locked"
```bash
rm geo.db-wal geo.db-shm
```

### مشکل: درخواست کند است
```sql
ANALYZE;  -- بازسازی شاخص‌ها
```

---

## 📦 فایل‌های تولید شده

بعد از راه‌اندازی، این فایل‌ها ایجاد می‌شوند:

| فایل | توضیح | اندازه |
|------|-------|--------|
| `geo.db` | پایگاه داده SQLite | ~15-20 MB |
| `bandar_places_knowledge.json` | دانشنامه جامع | ~5-10 MB |
| `bandar_places_search_index.json` | شاخص جستجو | ~2-3 MB |

---

## 🚀 موارد استفاده

### 1. سیستم جستجوی مکان‌ها
```python
with Places() as places:
    results = places.get_by_location(lat, lng, radius=5)
```

### 2. سیستم نقشه‌برداری
```python
with Analytics() as a:
    heatmap = a.get_places_heatmap()
```

### 3. سیستم تحلیل داده‌ها
```python
with Places() as places:
    stats = places.get_statistics()
```

### 4. سیستم راهنمایی گردشگران
```python
with Places() as places:
    hotels = places.get_by_category('hotel')
```

### 5. سیستم مدیریت شهری
```python
with Analytics() as a:
    overview = a.get_overview()
```

---

## 🤝 مشارکت

برای مشارکت:
1. Fork کنید
2. Branch جدید بسازید
3. تغییرات خود را انجام دهید
4. Pull Request ارسال کنید

---

## 📞 تماس و پشتیبانی

- 📧 **ایمیل:** hormozgamahdi@gmail.com
- 🐛 **Issues:** [GitHub Issues](https://github.com/hdpbnd/hermezgan-intelligent/issues)
- 🌐 **وب‌سایت:** [hormozgandriver.ir](http://hormozgandriver.ir)

---

## 📄 مجوز

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 تشکر

- داده‌های جغرافیایی هرمزگان
- OpenStreetMap
- SQLite Community

---

<div dir="rtl">

**ساخت شده با ❤️ برای شهر بندرعباس**

آخرین بروزرسانی: 2026-07-22

</div>
