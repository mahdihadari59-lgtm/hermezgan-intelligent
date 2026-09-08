# ============================================================
# copilot.py - اندپوینت Copilot Gateway
# پروژه هرمزگان هوشمند - Termux Android
# ============================================================
from __future__ import annotations

import os
import re
import json
import logging
import sqlite3
from typing import Optional, Any
from contextlib import contextmanager
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()

# ────────────────────────────────────────────────────────────
# مسیر دیتابیس
# ────────────────────────────────────────────────────────────
DB_PATH = "/data/data/com.termux/files/home/hormozgan_geo_project/hormozgan_data/hormozgan_master_final.db"

# ────────────────────────────────────────────────────────────
# اتصال به دیتابیس
# ────────────────────────────────────────────────────────────
@contextmanager
def get_db_connection():
    """مدیریت اتصال به دیتابیس SQLite"""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        yield conn
    except sqlite3.Error as e:
        logger.error(f"خطا در اتصال به دیتابیس: {e}")
        raise
    finally:
        if conn:
            conn.close()


def execute_query(query: str, params: tuple = ()) -> list[dict[str, Any]]:
    """اجرای کوئری امن و برگرداندن لیست دیکشنری"""
    with get_db_connection() as conn:
        cursor = conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def get_all_tables() -> list[str]:
    """دریافت لیست جداول کاربری (بدون سیستمی)"""
    query = """
        SELECT name FROM sqlite_master
        WHERE type='table'
          AND name NOT LIKE 'sqlite_%'
          AND name NOT LIKE 'rtree_%'
          AND name NOT LIKE '%_fts_%'
          AND name NOT LIKE 'backup_%'
        ORDER BY name
    """
    rows = execute_query(query)
    return [r["name"] for r in rows]


def get_table_schema(table_name: str) -> list[dict]:
    """دریافت ساختار ستون‌های یک جدول"""
    return execute_query(f"PRAGMA table_info({table_name})")


def get_table_count(table_name: str) -> int:
    """تعداد رکوردهای یک جدول"""
    rows = execute_query(f"SELECT COUNT(*) as cnt FROM {table_name}")
    return rows[0]["cnt"] if rows else 0


# ────────────────────────────────────────────────────────────
# نقشه معنایی کلمات کلیدی به جداول
# ────────────────────────────────────────────────────────────
KEYWORD_TABLE_MAP = {
    # گردشگری
    "گردشگری": ["tourism_poi", "tourism_food", "tourism_activities", "tourism_events", "tourist_areas", "natural_attractions", "cultural_sites"],
    "جاذبه": ["tourism_poi", "natural_attractions", "cultural_sites", "tourist_areas"],
    "جاذبه_گردشگری": ["tourism_poi", "natural_attractions", "cultural_sites"],
    "غذا": ["tourism_food", "restaurants", "cafes"],
    "غذای_محلی": ["tourism_food"],
    "فعالیت": ["tourism_activities"],
    "رویداد": ["tourism_events"],
    "جشنواره": ["tourism_events"],
    "هتل": ["hotels"],
    "اقامت": ["hotels"],
    "سوغات": ["souvenir_shops"],
    "بازار": ["markets", "shopping_centers"],
    "فروشگاه": ["markets", "shopping_centers", "boutiques"],

    # مسیریابی و ترافیک
    "مسیر": ["routes", "alternative_routes", "route_distances", "roads"],
    "مسیریابی": ["routes", "alternative_routes", "route_distances"],
    "راه": ["roads", "routes"],
    "جاده": ["roads", "routes"],
    "خیابان": ["roads"],
    "ترافیک": ["traffic_data", "traffic_info", "realtime_traffic", "traffic_devices"],
    "ترافیک_زنده": ["realtime_traffic"],
    "تصادف": ["accident_hotspots", "hotspots_info"],
    "نقطه_حادثه": ["accident_hotspots", "hotspots_info"],
    "دوربین": ["cameras_atlas", "cameras_info", "geo_reference_cameras_master"],
    "پارکینگ": ["parking_lots"],
    "پمپ_بنزین": ["fuel_stations"],
    "پل": ["bridges"],
    "میدان": ["squares"],

    # آموزش
    "مدرسه": ["schools", "public_schools", "private_schools", "technical_schools", "music_schools", "education", "education_geo"],
    "دانشگاه": ["universities", "education", "education_geo"],
    "آموزش": ["education", "education_geo", "educational_centers"],

    # بهداشت و درمان
    "بیمارستان": ["healthcare", "healthcare_geo", "medical_centers"],
    "درمان": ["healthcare", "healthcare_geo", "medical_centers", "therapy_clinics"],
    "داروخانه": ["pharmacies"],
    "پزشک": ["healthcare", "healthcare_geo"],
    "کلینیک": ["healthcare", "healthcare_geo", "therapy_clinics"],

    # اداری و خدماتی
    "بانک": ["banks", "geo_pois_master"],
    "اداره": ["offices"],
    "دفتر": ["offices"],
    "دادگستری": ["justice_sites"],
    "قضایی": ["justice_sites"],

    # حمل و نقل
    "حمل_ونقل": ["transport", "piers"],
    "اتوبوس": ["transport"],
    "اسکله": ["piers"],
    "بندر": ["piers"],

    # گویش بندری
    "بندری": ["bandari_vocabulary_master", "bandari_phrases_master", "bandari_dialogues_master", "bandari_proverbs_master", "bandari_grammar_master", "bandari_texts_master", "bandari_professional_terms_master"],
    "گویش": ["bandari_vocabulary_master", "dialect_comparison_master", "dialect_info_master"],
    "لهجه": ["dialect_comparison_master", "dialect_info_master"],
    "واژه": ["bandari_vocabulary_master"],
    "ضرب_المثل": ["bandari_proverbs_master"],
    "گرامر": ["bandari_grammar_master"],
    "گفتگو": ["bandari_dialogues_master"],

    # اطلاعات شهری
    "شهر": ["cities", "city_info", "city_history", "city_statistics"],
    "محله": ["neighborhoods", "neighborhoods_v3", "neighborhoods_detailed", "urban_areas", "urban_zones"],
    "منطقه": ["urban_zones", "urban_areas"],
    "پارک": ["parks"],
    "اماکن_مذهبی": ["religious_sites"],

    # صنعت
    "صنعت": ["industries"],
    "کارخانه": ["industries"],
    "زیرساخت": ["major_infrastructure"],

    # دانش و محتوا
    "دانش": ["knowledge", "knowledge_sources"],
    "مقاله": ["documents", "web_content"],
    "وب": ["web_content"],
    "محتوا": ["web_content", "documents"],
    "POI": ["pois", "poi_unified", "poi_descriptions"],
    "نقاط_علاقه": ["pois", "poi_unified"],
}


def detect_intent(message: str) -> list[str]:
    """تشخیص نیت کاربر و نگاشت به لیست جداول مرتبط"""
    msg_lower = message.lower().strip()
    matched_tables = set()

    for keyword, tables in KEYWORD_TABLE_MAP.items():
        keyword_parts = keyword.replace("_", " ").split()
        if any(part in msg_lower for part in keyword_parts):
            matched_tables.update(tables)

    if not matched_tables:
        matched_tables.update(get_all_tables())

    return list(matched_tables)


# ────────────────────────────────────────────────────────────
# توابع جستجو
# ────────────────────────────────────────────────────────────
def search_table(table_name: str, keywords: list[str], limit: int = 10) -> list[dict]:
    """جستجو در یک جدول خاص با کلمات کلیدی"""
    schema = get_table_schema(table_name)
    if not schema:
        return []

    text_cols = [c["name"] for c in schema if c["type"].upper() in ("TEXT", "VARCHAR")]
    if not text_cols:
        return []

    conditions = []
    params = []
    for col in text_cols:
        for kw in keywords:
            conditions.append(f'"{col}" LIKE ?')
            params.append(f"%{kw}%")

    if not conditions:
        return []

    query = f"""
        SELECT * FROM {table_name}
        WHERE {' OR '.join(conditions)}
        LIMIT {limit}
    """
    try:
        return execute_query(query, tuple(params))
    except Exception as e:
        logger.warning(f"خطا در جستجوی جدول {table_name}: {e}")
        return []


def search_fts_web_content(keywords: str, limit: int = 10) -> list[dict]:
    """جستجو در FTS5 وب‌کنتنت"""
    try:
        query = """
            SELECT w.* FROM web_content w
            JOIN web_content_fts fts ON w.id = fts.rowid
            WHERE web_content_fts MATCH ?
            LIMIT ?
        """
        return execute_query(query, (keywords, limit))
    except Exception as e:
        logger.warning(f"خطا در FTS web_content: {e}")
        return []


def search_fts_poi_descriptions(keywords: str, limit: int = 10) -> list[dict]:
    """جستجو در FTS5 توضیحات POI"""
    try:
        query = """
            SELECT p.* FROM poi_descriptions p
            JOIN poi_descriptions_fts fts ON p.rowid = fts.rowid
            WHERE poi_descriptions_fts MATCH ?
            LIMIT ?
        """
        return execute_query(query, (keywords, limit))
    except Exception as e:
        logger.warning(f"خطا در FTS poi_descriptions: {e}")
        return []


def search_geo_nearby(lat: float, lon: float, radius_km: float = 5.0, category: Optional[str] = None) -> list[dict]:
    """جستجوی مکان‌محور (هاورساین)"""
    delta = radius_km / 111.0

    tables = ["markets", "healthcare", "education", "transport", "hotels", "restaurants", "parks", "religious_sites"]
    if category:
        cat_map = {
            "بازار": "markets", "فروشگاه": "markets",
            "بیمارستان": "healthcare", "درمان": "healthcare", "داروخانه": "healthcare",
            "مدرسه": "education", "دانشگاه": "education",
            "هتل": "hotels", "رستوران": "restaurants", "پارک": "parks",
            "مذهبی": "religious_sites"
        }
        tables = [cat_map.get(category, category)] if category in cat_map else tables

    results = []
    for table in tables:
        try:
            query = f"""
                SELECT *, '{table}' as source_table FROM {table}
                WHERE lat BETWEEN ? AND ? AND lon BETWEEN ? AND ?
                LIMIT 20
            """
            rows = execute_query(query, (lat - delta, lat + delta, lon - delta, lon + delta))
            for r in rows:
                r["source_table"] = table
                results.append(r)
        except Exception:
            continue

    results.sort(key=lambda x: (x.get("lat", 0) - lat)**2 + (x.get("lon", 0) - lon)**2)
    return results[:20]


# ────────────────────────────────────────────────────────────
# توابع پاسخ‌دهی تخصصی
# ────────────────────────────────────────────────────────────
def get_traffic_status() -> dict:
    """وضعیت کلی ترافیک"""
    realtime = execute_query("SELECT * FROM realtime_traffic ORDER BY last_updated DESC LIMIT 10")
    alerts = execute_query("SELECT * FROM traffic_alerts LIMIT 10")
    patterns = execute_query("SELECT * FROM v_traffic_patterns ORDER BY high_pct DESC LIMIT 10")
    return {
        "realtime": realtime,
        "alerts": alerts,
        "patterns": patterns
    }


def get_safety_report() -> list[dict]:
    """گزارش ایمنی"""
    return execute_query("SELECT * FROM v_safety_report LIMIT 20")


def get_route_safety() -> list[dict]:
    """امنیت مسیرها"""
    return execute_query("SELECT * FROM v_route_safety LIMIT 20")


def get_city_info() -> dict:
    """اطلاعات کلی شهر بندرعباس"""
    info = execute_query("SELECT * FROM city_info LIMIT 1")
    stats = execute_query("SELECT * FROM city_statistics LIMIT 10")
    history = execute_query("SELECT * FROM city_history ORDER BY year DESC LIMIT 5")
    return {
        "info": info[0] if info else None,
        "statistics": stats,
        "history": history
    }


def get_bandari_info(query: str) -> dict:
    """جستجو در منابع گویش بندری"""
    keywords = [w for w in query.split() if len(w) > 2]
    results = {}
    tables = [
        "bandari_vocabulary_master", "bandari_phrases_master",
        "bandari_dialogues_master", "bandari_proverbs_master",
        "bandari_grammar_master", "bandari_texts_master",
        "bandari_professional_terms_master", "dialect_comparison_master"
    ]
    for table in tables:
        rows = search_table(table, keywords, limit=5)
        if rows:
            results[table] = rows
    return results


def get_tourism_info(keywords: list[str]) -> dict:
    """جستجو در اطلاعات گردشگری"""
    poi = search_table("tourism_poi", keywords, limit=10)
    food = search_table("tourism_food", keywords, limit=5)
    activities = search_table("tourism_activities", keywords, limit=5)
    events = search_table("tourism_events", keywords, limit=5)
    return {"poi": poi, "food": food, "activities": activities, "events": events}


# ────────────────────────────────────────────────────────────
# تولید پاسخ هوشمند
# ────────────────────────────────────────────────────────────
def build_response(intent: str, data: dict, message: str) -> dict:
    """ساخت پاسخ نهایی بر اساس نیت و داده‌ها"""
    response_text = f"🔍 نتیجه جستجو برای: «{message}»\n\n"

    if intent == "traffic":
        response_text += "🚦 **وضعیت ترافیک**\n"
        if data.get("realtime"):
            response_text += f"📊 {len(data['realtime'])} گزارش ترافیک زنده\n"
            for r in data["realtime"][:5]:
                response_text += f"  • {r.get('road_name', '---')}: {r.get('traffic_level', '---')} ({r.get('speed_kmh', '?')} km/h)\n"
        if data.get("alerts"):
            response_text += f"\n⚠️ {len(data['alerts'])} هشدار ترافیکی\n"

    elif intent == "tourism":
        response_text += "🌴 **اطلاعات گردشگری**\n"
        total = sum(len(v) for v in data.values() if isinstance(v, list))
        response_text += f"📍 {total} مورد یافت شد\n"
        for key, items in data.items():
            if items:
                response_text += f"\n▸ {key}: {len(items)} مورد\n"
                for item in items[:3]:
                    name = item.get("name_fa") or item.get("name") or item.get("title") or "---"
                    response_text += f"   • {name}\n"

    elif intent == "bandari":
        response_text += "🗣️ **گویش بندری**\n"
        total = sum(len(v) for v in data.values())
        response_text += f"📚 {total} نتیجه در منابع بندری\n"
        for table, items in data.items():
            if items:
                response_text += f"\n▸ {table}: {len(items)} مورد\n"
                for item in items[:2]:
                    word = item.get("word_bandari") or item.get("phrase_bandari") or item.get("proverb_bandari") or "---"
                    meaning = item.get("word_persian") or item.get("phrase_persian") or item.get("proverb_persian") or ""
                    response_text += f"   • {word} = {meaning[:50]}\n"

    elif intent == "safety":
        response_text += "🛡️ **گزارش ایمنی**\n"
        if data.get("safety_report"):
            for r in data["safety_report"][:5]:
                response_text += f"  • {r.get('hotspot_name', '---')}: {r.get('equipment_status', '---')}\n"

    elif intent == "city_info":
        info = data.get("info", {})
        response_text += "🏙️ **اطلاعات شهر**\n"
        if info:
            response_text += f"  نام: {info.get('city_name', '---')}\n"
            response_text += f"  جمعیت: {info.get('population_2026', '---')}\n"
            response_text += f"  مساحت: {info.get('area_km2', '---')} km²\n"

    else:
        total = sum(len(v) for v in data.values() if isinstance(v, list))
        response_text += f"📊 {total} نتیجه در دیتابیس یافت شد\n"
        for table, items in data.items():
            if items and isinstance(items, list):
                response_text += f"\n▸ {table}: {len(items)} مورد\n"
                for item in items[:3]:
                    name = item.get("name_fa") or item.get("name") or item.get("title") or str(item)[:50]
                    response_text += f"   • {name}\n"

    return {
        "status": "success",
        "message": response_text,
        "data": data,
        "intent": intent
    }


# ────────────────────────────────────────────────────────────
# مدل‌های Pydantic
# ────────────────────────────────────────────────────────────
class CopilotMessageRequest(BaseModel):
    text: str
    session_id: Optional[str] = None
    user_id: Optional[str] = "anonymous"
    location: Optional[dict] = None  # {"lat": 27.18, "lon": 56.28}


# ────────────────────────────────────────────────────────────
# اندپوینت‌ها
# ────────────────────────────────────────────────────────────
@router.post("/message")
async def copilot_message(payload: CopilotMessageRequest):
    """پردازش پیام از طریق Copilot Gateway"""
    try:
        message = payload.text.strip()
        user_id = payload.user_id or "anonymous"
        session_id = payload.session_id
        location = payload.location

        # بررسی وجود دیتابیس
        if not os.path.exists(DB_PATH):
            raise HTTPException(status_code=500, detail=f"❌ دیتابیس یافت نشد: {DB_PATH}")

        # ── دستورات خاص ──
        msg_lower = message.lower()

        # لیست جداول
        if any(k in msg_lower for k in ["لیست جداول", "جدول ها", "tables", "جداول"]):
            tables = get_all_tables()
            return {
                "status": "success",
                "message": f"📋 {len(tables)} جدول در دیتابیس:\n" + "\n".join(f"  • {t}" for t in tables),
                "data": {"tables": tables, "count": len(tables)},
                "session_id": session_id, "user_id": user_id
            }

        # ساختار جدول
        if any(k in msg_lower for k in ["ساختار", "schema", "ستون"]):
            for table in get_all_tables():
                if table.lower() in msg_lower:
                    schema = get_table_schema(table)
                    count = get_table_count(table)
                    lines = [f"  {c['name']} ({c['type']})" for c in schema]
                    return {
                        "status": "success",
                        "message": f"📐 جدول '{table}' ({count} رکورد):\n" + "\n".join(lines),
                        "data": {"table": table, "schema": schema, "count": count},
                        "session_id": session_id, "user_id": user_id
                    }
            return {"status": "success", "message": "❌ جدولی یافت نشد", "data": None, "session_id": session_id, "user_id": user_id}

        # وضعیت ترافیک
        if any(k in msg_lower for k in ["ترافیک", "ترافیک زنده", "traffic", "شلوغی"]):
            data = get_traffic_status()
            result = build_response("traffic", data, message)
            result["session_id"] = session_id
            result["user_id"] = user_id
            return result

        # ایمنی
        if any(k in msg_lower for k in ["ایمنی", "حادثه", "تصادف", "safety", "accident"]):
            safety = get_safety_report()
            routes = get_route_safety()
            result = build_response("safety", {"safety_report": safety, "route_safety": routes}, message)
            result["session_id"] = session_id
            result["user_id"] = user_id
            return result

        # اطلاعات شهر
        if any(k in msg_lower for k in ["شهر", "بندرعباس", "اطلاعات شهر", "city info"]):
            data = get_city_info()
            result = build_response("city_info", data, message)
            result["session_id"] = session_id
            result["user_id"] = user_id
            return result

        # گویش بندری
        if any(k in msg_lower for k in ["بندری", "گویش", "لهجه", "ضرب المثل", "واژه بندری", "bandari"]):
            data = get_bandari_info(message)
            result = build_response("bandari", data, message)
            result["session_id"] = session_id
            result["user_id"] = user_id
            return result

        # گردشگری
        if any(k in msg_lower for k in ["گردشگری", "جاذبه", "غذا محلی", "هتل", "tourism", "attraction", "hotel", "food"]):
            keywords = [w for w in message.split() if len(w) > 2]
            data = get_tourism_info(keywords)
            result = build_response("tourism", data, message)
            result["session_id"] = session_id
            result["user_id"] = user_id
            return result

        # جستجوی مکان‌محور
        if location and location.get("lat") and location.get("lon"):
            lat, lon = location["lat"], location["lon"]
            nearby = search_geo_nearby(lat, lon, radius_km=5.0)
            return {
                "status": "success",
                "message": f"📍 {len(nearby)} مکان در شعاع ۵ کیلومتری شما:\n" + "\n".join(
                    f"  • {r.get('name_fa') or r.get('name') or '---'} ({r.get('source_table', '---')})"
                    for r in nearby[:10]
                ),
                "data": {"nearby": nearby, "location": location},
                "session_id": session_id, "user_id": user_id
            }

        # ── جستجوی عمومی هوشمند ──
        keywords = [w for w in re.findall(r'[\u0600-\u06FF\w]{3,}', message)]
        if not keywords:
            keywords = message.split()

        target_tables = detect_intent(message)
        results = {}
        total_found = 0

        for table in target_tables:
            rows = search_table(table, keywords, limit=10)
            if rows:
                results[table] = rows
                total_found += len(rows)

        # جستجو در FTS
        fts_query = " ".join(keywords)
        web_fts = search_fts_web_content(fts_query, limit=10)
        if web_fts:
            results["web_content_fts"] = web_fts
            total_found += len(web_fts)

        poi_fts = search_fts_poi_descriptions(fts_query, limit=10)
        if poi_fts:
            results["poi_descriptions_fts"] = poi_fts
            total_found += len(poi_fts)

        if total_found > 0:
            result = build_response("general", results, message)
            result["session_id"] = session_id
            result["user_id"] = user_id
            return result
        else:
            all_tables = get_all_tables()
            return {
                "status": "success",
                "message": f"❌ نتیجه‌ای برای '{message}' یافت نشد.\n\n💡 جداول موجود: {', '.join(all_tables[:20])}...",
                "data": {"query": message, "keywords": keywords, "tables": all_tables},
                "session_id": session_id, "user_id": user_id
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"خطا در copilot gateway: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"❌ خطای داخلی: {e}")


# ────────────────────────────────────────────────────────────
# اندپوینت سلامت
# ────────────────────────────────────────────────────────────
@router.get("/health")
async def health_check():
    """بررسی سلامت سرویس و دیتابیس"""
    try:
        tables = get_all_tables()
        total_records = sum(get_table_count(t) for t in tables)
        db_exists = os.path.exists(DB_PATH)
        return {
            "status": "healthy" if db_exists else "unhealthy",
            "database_path": DB_PATH,
            "database_exists": db_exists,
            "tables_count": len(tables),
            "total_records_estimate": total_records,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {e}")
