# راهنمای سریع استفاده از GEO.DB

## 📋 خلاصه

پروژه **GEO.DB** پایگاه داده جغرافیایی جامع برای شهر بندرعباس و استان هرمزگان است.

شامل:
- ✅ **677 مکان** در بندرعباس (رستوران، کافه، هتل، بیمارستان، و غیره)
- ✅ **13 شهرستان** هرمزگان
- ✅ **14 جزیره** اصلی
- ✅ **R-Tree Indexing** برای جستجوی مکانی سریع
- ✅ **Python API** برای دسترسی آسان

---

## 🚀 نصب و راه‌اندازی

### مرحله ۱: مقداردهی اولیه پایگاه داده

```bash
# ایجاد و راه‌اندازی پایگاه داده
python3 init_geodb.py

# یا اجباری بازنشانی (اگر پایگاه قبلاً وجود داشت)
python3 init_geodb.py --force
```

### مرحله ۲: وارد کردن داده‌های جغرافیایی

```bash
# وارد کردن شهرستان‌ها و جزایر
python3 import_hormozgan_atlas.py \
  --db geo.db \
  --atlas hormozgan_atlas_dictionary.json

# وارد کردن 677 مکان بندرعباس
python3 import_bandar_places.py \
  --db geo.db \
  --places bandar_places.json
```

### مرحله ۳: ایجاد دانشنامه و شاخص جستجو

```bash
# ایجاد دانشنامه جامع و شاخص جستجو
python3 generate_places_kb.py --db geo.db
```

---

## 💻 استفاده از Python API

### نمونه ۱: جستجو در مکان‌ها

```python
from geodb import Places

# باز کردن اتصال
with Places() as places:
    # جستجو بر اساس نام
    cafes = places.search_by_name("کافه")
    print(f"یافت شد: {len(cafes)} کافه")
    for cafe in cafes[:3]:
        print(f"  • {cafe['name']} - {cafe['lat']}, {cafe['lng']}")
    
    # دریافت تمام دسته‌ها
    categories = places.get_categories()
    for cat in categories[:5]:
        print(f"{cat['icon']} {cat['category_name']}: {cat['count']} مورد")
```

### نمونه ۲: جستجوی مکانی (Spatial Query)

```python
from geodb import Places

# یافتن همه رستوران‌ها در شعاع 5 کیلومتری
with Places() as places:
    # بندرعباس مرکز: 27.1842, 56.2893
    nearby = places.get_by_location(27.1842, 56.2893, radius_km=5.0)
    
    print(f"مکان‌های نزدیک:")
    for place in nearby:
        print(f"  {place['icon']} {place['name']}")
        print(f"     فاصله: {place['distance_km']:.2f} کیلومتر")
        print(f"     دسته: {place['category_name']}\n")
```

### نمونه ۳: دریافت شهرستان‌ها

```python
from geodb import Counties, Islands

# تمام شهرستان‌ها
with Counties() as counties:
    all_counties = counties.get_all()
    for county in all_counties:
        print(f"{county['name']}: {county['center']}")

# جزایر یک شهرستان
with Islands() as islands:
    qeshm_islands = islands.get_by_county("قشم")
    print(f"جزایر قشم:")
    for island in qeshm_islands:
        print(f"  • {island['name']}")
```

### نمونه ۴: تحلیل و آمار

```python
from geodb import Analytics, Places

# نمای کلی پایگاه داده
with Analytics() as analytics:
    overview = analytics.get_overview()
    print(f"📊 خلاصه پایگاه داده:")
    for table, count in overview.items():
        print(f"  {table}: {count}")

# آمار مکان‌ها
with Places() as places:
    stats = places.get_statistics()
    print(f"\n📍 آمار مکان‌ها:")
    print(f"  کل مکان‌ها: {stats['total']}")
    print(f"  دسته‌ها: {', '.join(stats['by_category'].keys())}")
```

---

## 🔍 نمونه‌های SQL

### نمونه ۱: تمام کافه‌های بندرعباس

```sql
SELECT name, lat, lng FROM places
WHERE category = 'cafe'
ORDER BY name;
```

### نمونه ۲: مکان‌های در یک منطقه (Bounding Box)

```sql
SELECT * FROM places
WHERE lat BETWEEN 27.1 AND 27.2
  AND lng BETWEEN 56.2 AND 56.4
ORDER BY name;
```

### نمونه ۳: جستجوی سریع با R-Tree

```sql
SELECT p.* FROM places p
JOIN places_rtree pr ON p.id = pr.id
WHERE pr.min_lat BETWEEN 27.0 AND 27.3
  AND pr.min_lng BETWEEN 56.0 AND 56.5;
```

### نمونه ۴: آمار مکان‌ها بر حسب دسته

```sql
SELECT category_name, COUNT(*) as count, icon
FROM places
GROUP BY category_name
ORDER BY count DESC;
```

### نمونه ۵: تمام جزایر و شهرستان آن

```sql
SELECT gi.name as island, gc.name as county
FROM geo_islands gi
JOIN geo_counties gc ON gi.county_id = gc.id
ORDER BY gc.name, gi.name;
```

---

## 📁 ساختار فایل‌ها

```
hermezgan-intelligent/
├── database/
│   ├── schema.sql                    # اسکیمای اصلی (POIs، ترافیک، دوربین، و غیره)
│   └── schema_admin_geo.sql          # اسکیمای جغرافیایی (شهرستان‌ها، جزایر)
├── init_geodb.py                     # مقداردهی اولیه پایگاه داده
├── import_hormozgan_atlas.py         # وارد کردن اطلاعات هرمزگان
├── import_bandar_places.py           # وارد کردن 677 مکان بندرعباس
├── generate_places_kb.py             # ایجاد دانشنامه و شاخص
├── geodb.py                          # ماژول Python برای دسترسی
├── hormozgan_atlas_dictionary.json   # داده‌های جغرافیایی
├── bandar_places.json                # داده‌های 677 مکان
├── geo.db                            # پایگاه داده SQLite (تولید شده)
├── bandar_places_knowledge.json      # دانشنامه مکان‌ها (تولید شده)
└── bandar_places_search_index.json   # شاخص جستجو (تولید شده)
```

---

## 🎯 دسته‌های مکان

| کد | نام فارسی | نماد | تعداد |
|----|-----------|------|-------|
| cafe | کافه‌ها و چایخانه‌ها | ☕ | ~50 |
| restaurant | رستوران‌ها و غذاخوری‌ها | 🍽️ | ~120 |
| hotel | هتل‌ها و اقامتگاه‌ها | 🏨 | ~80 |
| hospital | بیمارستان‌ها و مراکز درمانی | 🏥 | ~30 |
| pharmacy | داروخانه‌ها | 💊 | ~40 |
| bank | بانک‌ها و مؤسسات مالی | 🏦 | ~35 |
| fuel | پمپ بنزین‌ها و جایگاه‌های سوخت | ⛽ | ~25 |
| school | مدارس و مراکز آموزشی | 🏫 | ~80 |
| police | کلانتری‌ها و مراکز پلیس | 👮 | ~15 |
| park | پارک‌ها و بوستان‌ها | 🌳 | ~40 |
| market | بازارها و مراکز خرید | 🛍️ | ~60 |
| mosque | مساجد و اماکن مذهبی | 🕌 | ~50 |
| parking | پارکینگ‌ها | 🅿️ | ~35 |
| bus_station | پایانه‌های مسافربری | 🚌 | ~10 |
| atm | خودپردازها | 💰 | ~45 |

---

## 🔧 مثال‌های عملی

### جستجو برای رستوران‌های دریایی

```python
from geodb import Places

with Places() as places:
    restaurants = places.get_by_category('restaurant')
    seafood = [r for r in restaurants 
               if 'دریایی' in r['name'] or 'ماهی' in r['name']]
    
    print(f"رستوران‌های دریایی: {len(seafood)}")
    for r in seafood[:5]:
        print(f"  • {r['name']}")
```

### یافتن نزدیک‌ترین بیمارستان

```python
from geodb import Places
import heapq

def nearest_hospital(lat, lng, n=3):
    with Places() as places:
        hospitals = places.get_by_location(lat, lng, radius_km=20)
        return heapq.nsmallest(n, hospitals, 
                               key=lambda x: x['distance_km'])

# نزدیک‌ترین بیمارستان به فرودگاه
nearby = nearest_hospital(27.1, 56.4, n=3)
for h in nearby:
    print(f"{h['name']}: {h['distance_km']:.2f} کیلومتر")
```

### نقشه گرمایی مکان‌ها

```python
from geodb import Analytics

with Analytics() as analytics:
    heatmap = analytics.get_places_heatmap(zoom_level=2)
    
    print("توزیع مکان‌ها:")
    for cell in heatmap[:10]:
        print(f"  منطقه ({cell['lat_cell']}, {cell['lng_cell']}): "
              f"{cell['count']} مکان ({cell['category_name']})")
```

---

## ⚡ نکات عملکرد

- **R-Tree Indexing**: جستجوهای مکانی در کمتر از ۱ میلی‌ثانیه
- **WAL Mode**: حمایت از دسترسی‌های همزمان
- **Foreign Keys**: تضمین یکپارچگی داده‌ها
- **JSON Storage**: فضای سبک برای برچسب‌های اضافی

---

## 📞 پشتیبانی

برای مسائل و پیشنهادات:
- 📧 ایمیل: hormozgamahdi@gmail.com
- 🐛 Issues: https://github.com/hdpbnd/hermezgan-intelligent/issues

---

## 📄 مجوز

This project is licensed under the MIT License - see the LICENSE file for details.
