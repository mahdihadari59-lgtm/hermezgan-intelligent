#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌊 HDP AI v6.0 - Dual Database Bandari Dialect AI System
"""

import sqlite3
import os
import time
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

import math


def _haversine_km(lat1, lon1, lat2, lon2):
    """محاسبه فاصله بین دو نقطه جغرافیایی به کیلومتر"""
    if None in (lat1, lon1, lat2, lon2):
        return None
    try:
        lat1, lon1, lat2, lon2 = float(lat1), float(lon1), float(lat2), float(lon2)
    except (TypeError, ValueError):
        return None
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    return R * 2 * math.asin(math.sqrt(a))

# ============================================================
# تنظیمات مسیر دیتابیس‌ها
# ============================================================

BASE_DIR = Path(__file__).parent

BANDARI_DB_PATH = str(BASE_DIR / "bandari.db")
HORMOZGAN_DB_PATH = "/data/data/com.termux/files/home/hormozgan_geo_project/hormozgan_data/hormozgan_master_final.db"


# ============================================================
# کلاس اصلی
# ============================================================

class HDPAIV6Dual:
    def __init__(self):
        self.bandari_db = BANDARI_DB_PATH
        self.hormozgan_db = HORMOZGAN_DB_PATH
        self._dictionary = {}
        self._history = []
        self._load_dictionary()
        print(f"✅ دیتابیس بندری: {self.bandari_db}")
        print(f"✅ دیتابیس هرمزگان: {self.hormozgan_db}")
    
    def _load_dictionary(self):
        """بارگذاری دیکشنری از دیتابیس بندری"""
        try:
            conn = sqlite3.connect(self.bandari_db)
            cursor = conn.cursor()
            cursor.execute("SELECT word_standard, word_bandari, dialect_code FROM bandari_words")
            for row in cursor.fetchall():
                self._dictionary[row[0]] = {'bandari': row[1], 'dialect': row[2]}
            conn.close()
            print(f"   📖 {len(self._dictionary)} کلمه بارگذاری شد")
        except Exception as e:
            print(f"   ⚠️ خطا در بارگذاری دیکشنری: {e}")
    
    def check_databases(self):
        """بررسی وجود دیتابیس‌ها"""
        results = {}
        
        # بررسی دیتابیس بندری
        if os.path.exists(self.bandari_db):
            results['bandari'] = {'exists': True, 'path': self.bandari_db}
            try:
                conn = sqlite3.connect(self.bandari_db)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM bandari_words")
                results['bandari']['words'] = cursor.fetchone()[0]
                conn.close()
            except Exception as e:
                results['bandari']['words'] = f'error: {e}'
        else:
            results['bandari'] = {'exists': False, 'path': self.bandari_db}
        
        # بررسی دیتابیس هرمزگان
        if os.path.exists(self.hormozgan_db):
            results['hormozgan'] = {'exists': True, 'path': self.hormozgan_db}
            try:
                conn = sqlite3.connect(self.hormozgan_db)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 10")
                tables = [row[0] for row in cursor.fetchall()]
                results['hormozgan']['tables'] = tables
                conn.close()
            except Exception as e:
                results['hormozgan']['tables'] = f'error: {e}'
        else:
            results['hormozgan'] = {'exists': False, 'path': self.hormozgan_db}
        
        return results
    
    def process(self, text: str, user_lat=None, user_lon=None):
        """پردازش پیام کاربر"""
        @dataclass
        class Response:
            input_text: str
            intent: str
            confidence: float
            dialect: str
            results: List[Dict]
            translation: Optional[str]
            response: str
            elapsed_ms: float
            timestamp: str
        
        start_time = time.time()
        
        # تشخیص گویش
        dialect = self._detect_dialect(text)
        
        # ترجمه
        translation = self._translate(text)
        
        # جستجو در دیتابیس هرمزگان
        results = self._search_hormozgan(text, user_lat=user_lat, user_lon=user_lon)
        
        # تولید پاسخ
        response_text = self._generate_response(text, results, translation)
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        return Response(
            input_text=text,
            intent='general',
            confidence=0.5,
            dialect=dialect,
            results=results,
            translation=translation,
            response=response_text,
            elapsed_ms=round(elapsed_ms, 2),
            timestamp=datetime.now().isoformat()
        )
    
    def _detect_dialect(self, text: str) -> str:
        """تشخیص گویش از متن"""
        dialect_keywords = {
            'ban': ['براری', 'ابی', 'چش', 'هو', 'بندری'],
            'min': ['چکری', 'مینابی'],
            'qes': ['قشمی'],
            'jas': ['جاسکی'],
            'lan': ['لنگه'],
            'bas': ['بستکی'],
            'kha': ['خمیری'],
            'rud': ['چگری', 'رودانی'],
            'sir': ['سیریکی']
        }
        for dialect, keywords in dialect_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return dialect
        return 'ban'
    
    def _translate(self, text: str) -> Optional[str]:
        """ترجمه به بندری"""
        words = text.split()
        translated = []
        for word in words:
            clean = word.strip('.,!?')
            if clean in self._dictionary:
                translated.append(self._dictionary[clean]['bandari'])
            else:
                translated.append(clean)
        result = ' '.join(translated)
        return result if result != text else None
    
    STOPWORDS = {
        'کجاست', 'چطوره', 'میخوام', 'می\u200cخوام', 'خرید', 'کنم',
        'برای', 'من', 'است', 'هست', 'یک', 'چی', 'کو', 'نزدیک', 'ترین',
        'خوب', 'معرفی', 'کن', 'بگو', 'میکنم', 'می\u200cکنم', 'رو', 'به',
        'از', 'با', 'را', 'در', 'که', 'این', 'آن'
    }

    SEARCH_TABLES = [
        ("pois", "name", "cat", "city", "district", "address", "lat", "lon"),
        ("healthcare", "name", "type", "city", "district", "address", "lat", "lon"),
        ("markets", "name_fa", "shop_type", "city", "district", None, "lat", "lon"),
        ("restaurants", "name", "cuisine", "city", "district", "address", "lat", "lon"),
        ("banks", "name", "type", "city", "district", "address", "lat", "lon"),
        ("pharmacies", "name", "type", "city", "district", "address", "lat", "lon"),
        ("hotels", "name", "type", "city", "district", "address", "lat", "lon"),
        ("schools", "name", "type", "city", "district", "address", "lat", "lon"),
    ]

    def _extract_keywords(self, text: str) -> List[str]:
        """استخراج کلمات کلیدی معنادار از جمله"""
        words = [w.strip('؟?!.,،') for w in text.split()]
        keywords = [w for w in words if w and w not in self.STOPWORDS and len(w) > 1]
        return keywords or [text]

    def _search_hormozgan(self, text: str, user_lat=None, user_lon=None) -> List[Dict]:
        """جستجوی چندجدولی، چندکلمه‌ای و مکان‌محور در دیتابیس هرمزگان"""
        results = []
        if not os.path.exists(self.hormozgan_db):
            return results

        keywords = self._extract_keywords(text)

        try:
            conn = sqlite3.connect(self.hormozgan_db)
            cursor = conn.cursor()

            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = {row[0] for row in cursor.fetchall()}

            for table, name_col, cat_col, city_col, dist_col, addr_col, lat_col, lon_col in self.SEARCH_TABLES:
                if table not in existing_tables:
                    continue

                addr_select = f", {addr_col}" if addr_col else ", NULL"
                sql = f"""
                    SELECT {name_col}, {cat_col}, {city_col}, {dist_col}{addr_select}, {lat_col}, {lon_col}
                    FROM {table}
                    WHERE ({name_col} IS NOT NULL AND {name_col} != '')
                """
                keyword_conditions = " OR ".join(
                    [f"{name_col} LIKE ? OR {cat_col} LIKE ? OR {city_col} LIKE ?" for _ in keywords]
                )
                sql += f" AND ({keyword_conditions}) LIMIT 20"

                params = []
                for kw in keywords:
                    params.extend([f"%{kw}%", f"%{kw}%", f"%{kw}%"])

                try:
                    cursor.execute(sql, params)
                    for row in cursor.fetchall():
                        name = row[0]
                        if not name:
                            continue
                        r_lat, r_lon = row[5], row[6]
                        distance_km = _haversine_km(user_lat, user_lon, r_lat, r_lon)

                        category = (row[1] or '').lower()
                        category_match = any(kw.lower() in category for kw in keywords)

                        results.append({
                            'type': table,
                            'name': name,
                            'category': row[1] or 'عمومی',
                            'city': row[2] or '',
                            'district': row[3] or '',
                            'address': row[4] or '',
                            'distance_km': round(distance_km, 2) if distance_km is not None else None,
                            '_category_match': category_match,
                        })
                except Exception:
                    continue

            conn.close()
        except Exception as e:
            print(f"⚠️ خطا در جستجوی هرمزگان: {e}")

        # اولویت‌بندی: اول category match، بعد نزدیک‌ترین (اگر مختصات کاربر موجود بود)
        def sort_key(r):
            cat_priority = 0 if r['_category_match'] else 1
            dist = r['distance_km'] if r['distance_km'] is not None else float('inf')
            return (cat_priority, dist)

        results.sort(key=sort_key)

        for r in results:
            r.pop('_category_match', None)

        return results[:5]

    def _generate_response(self, text: str, results: List[Dict], translation: Optional[str]) -> str:
        """تولید پاسخ"""
        # احوالپرسی
        if 'سلام' in text:
            return "سَلام! خوش آمدید به سرویس هوشمند بندری. چطور می‌توانم کمک کنم؟"
        elif 'چطوری' in text or 'خوبی' in text:
            return "خوبم، ممنون! شما چطورید؟"
        elif 'خداحافظ' in text:
            return "خدا نگهدار! بازم سر بزنید."
        elif 'ممنون' in text:
            return "خواهش می‌کنم! خوشحالم که کمک کردم."
        
        # ترجمه
        if translation:
            return f"🔤 ترجمه به بندری: «{translation}»"
        
        # نتایج جستجو
        if results:
            lines = []
            for r in results[:3]:
                name = r.get('name', '')
                city = r.get('city', '')
                cat = r.get('category', '')
                lines.append(f"📍 {name} ({city}) - {cat}")
            return '\n'.join(lines)
        
        # پاسخ پیش‌فرض
        return "در حال جستجو در دیتابیس هرمزگان هستم. لطفاً دقیق‌تر بپرسید."


# ============================================================
# رابط خط فرمان
# ============================================================

def main():
    print("=" * 60)
    print("🌊 HDP AI v6.0 - Dual Database Bandari Dialect AI System")
    print("=" * 60)
    
    ai = HDPAIV6Dual()
    stats = ai.check_databases()
    
    print("\n📊 وضعیت دیتابیس‌ها:")
    for name, info in stats.items():
        status = "✅" if info['exists'] else "❌"
        print(f"   {status} {name}:")
        print(f"      مسیر: {info['path']}")
        if info['exists']:
            if name == 'bandari' and 'words' in info:
                print(f"      کلمات: {info['words']}")
            if name == 'hormozgan' and 'tables' in info:
                tables = info['tables']
                print(f"      جدول‌ها: {tables[:3] if tables else 'هیچ'}...")
    
    print("\n💬 برای شروع تایپ کنید (exit برای خروج)")
    print("-" * 60)
    
    while True:
        try:
            user_input = input("\n👤 شما: ").strip()
            if user_input.lower() in ['exit', 'quit', 'خروج']:
                print("👋 خداحافظ! خدا نگهدار!")
                break
            if not user_input:
                continue
            
            r = ai.process(user_input)
            print(f"\n🤖 پاسخ:")
            print(f"   🗣️ گویش: {r.dialect}")
            if r.translation:
                print(f"   🔤 ترجمه: {r.translation}")
            if r.results:
                print(f"   📚 نتایج: {len(r.results)} مورد")
            print(f"\n📝 {r.response}")
            print(f"\n⏱️ {r.elapsed_ms:.2f} ms")
            
        except KeyboardInterrupt:
            print("\n👋 خداحافظ!")
            break
        except Exception as e:
            print(f"❌ خطا: {e}")

if __name__ == "__main__":
    main()
