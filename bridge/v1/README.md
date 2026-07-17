# HDP Database Bridge v1

## Overview

HDP Database Bridge یک لایه ارتباطی بین دو پایگاه داده SQLite است.

```
geo.db
        ⇄
DatabaseBridge
        ⇄
hdp_v2.db
```

این Bridge از قابلیت Native SQLite ATTACH DATABASE استفاده می‌کند.

---

## اهداف

- عدم کپی داده
- عدم تغییر Schema
- عدم Migration
- فقط خواندن (Read Only)
- سرعت بالا
- قابل استفاده در Termux
- قابل استفاده در Linux
- قابل استفاده در cPanel

---

## ساختار

bridge/
└── v1/
    ├── __init__.py
    ├── config.py
    ├── database_bridge.py
    ├── bridge_example.py
    ├── test_database_bridge.py
    ├── README.md
    └── tests/

---

## Databases

### Geo Database

```
geo.db
```

Contains:

- roads
- hospitals
- traffic cameras
- tourism
- geometry
- spatial indexes

---

### Knowledge Database

```
hdp_v2.db
```

Contains:

- knowledge
- knowledge_relations
- entities
- graph
- AI knowledge

---

## Principle

No record is copied.

No database is modified.

SQLite opens geo.db as:

```
main
```

and attaches:

```
knowledge
```

using

```sql
ATTACH DATABASE
```


HDP Database Bridge v1

هدف

این ماژول یک لایه اتصال بین دو پایگاه داده مستقل است:

geo.db

hdp_v2.db

بدون انتقال اطلاعات.

وظایف

اتصال همزمان به چند SQLite Database

ATTACH DATABASE

اجرای JOIN بین دیتابیس‌ها

عدم ایجاد وابستگی به HDP Core

عدم وابستگی به geo package

عدم تغییر ساختار دیتابیس‌ها

فقط خواندن و Query

معماری

bridge/
│
├── config.py
├── database_bridge.py
├── bridge_example.py
├── test_database_bridge.py
└── tests/

اصول طراحی

Independent

Read Only

Thread Safe

Modular

Reusable

نسخه

v1.0

Designed for Hormozgan Driver Pro
