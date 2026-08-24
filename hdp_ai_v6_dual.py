#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌊 HDP AI v6.0 - Dual Database Bandari Dialect AI System
هوش مصنوعی حرفه‌ای با پشتیبانی از دو دیتابیس:
  1. bandari.db - واژگان و گویش بندری
  2. hormozgan_master_final.db - اطلاعات جغرافیایی و گردشگری هرمزگان
"""

import sqlite3
import json
import re
import unicodedata
import os
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path

# ============================================================
# تنظیمات مسیر دیتابیس‌ها
# ============================================================

BASE_DIR = Path(__file__).parent

# دیتابیس اول: واژگان بندری
BANDARI_DB_PATH = str(BASE_DIR / "bandari.db")

# دیتابیس دوم: اطلاعات جغرافیایی هرمزگان
HORMOZGAN_DB_PATH = "/data/data/com.termux/files/home/hormozgan_geo_project/hormozgan_data/hormozgan_master_final.db"

# مسیر فایل‌های داده
DATA_DIR = Path("/data/data/com.termux/files/home/hermezgan-intelligent/integrations/bandari-engine-v5.2.0")


# ============================================================
# ۱. نرمالایزر متن (با پشتیبانی از گویش‌ها)
# ============================================================

class TextNormalizer:
    """نرمالایزر پیشرفته برای متن فارسی و ۹ گویش بندری"""
    
    def __init__(self):
        self.arabic_to_persian = {
            'ك': 'ک', 'ي': 'ی', 'ة': 'ه',
            'أ': 'ا', 'إ': 'ا', 'آ': 'آ',
            'ؤ': 'و', 'ئ': 'ی'
        }
        self.diacritics = re.compile(r'[\u064B-\u065F\u0670\u0640]')
        self.extra_spaces = re.compile(r'\s{2,}')
        self.control_chars = re.compile(r'[\x00-\x1F\x7F-\x9F]')
        
        # گویش‌های پشتیبانی‌شده
        self.dialects = {
            'ban': 'بندری',
            'min': 'مینابی',
            'qes': 'قشمی',
            'jas': 'جاسکی',
            'lan': 'لنگه‌ای',
            'bas': 'بستکی',
            'kha': 'خمیری',
            'rud': 'رودانی',
            'sir': 'سیریکی'
        }
        
        # کلمات کلیدی تشخیص گویش
        self.dialect_keywords = {
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
    
    def normalize(self, text: str) -> str:
        """نرمالایز کامل متن"""
        if not text:
            return ""
        
        result = text
        result = self.control_chars.sub('', result)
        
        for arabic, persian in self.arabic_to_persian.items():
            result = result.replace(arabic, persian)
        
        result = self.diacritics.sub('', result)
        result = self.extra_spaces.sub(' ', result)
        
        return result.strip()
    
    def normalize_for_match(self, text: str) -> str:
        """نرمالایز برای تطبیق"""
        result = self.normalize(text)
        result = result.replace('\u200c', '')
        return result.lower()
    
    def detect_dialect(self, text: str) -> str:
        """تشخیص گویش از متن"""
        text = self.normalize(text)
        for dialect, keywords in self.dialect_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return dialect
        return 'ban'


# ============================================================
# ۲. موتور تشخیص نیت
# ============================================================

class IntentEngine:
    """تشخیص نیت کاربر با پشتیبانی از گویش بندری"""
    
    def __init__(self):
        self.intents = {
            'traffic': {
                'keywords': ['ترافیک', 'جاده', 'تصادف', 'راه', 'رانندگی', 'مسیر', 'بسته', 'شلوغ', 'خون جاده'],
                'weight': 1.2
            },
            'health': {
                'keywords': ['بیمارستان', 'درمانگاه', 'داروخانه', 'دکتر', 'اورژانس', 'کلینیک', 'مریض'],
                'weight': 1.3
            },
            'tourism': {
                'keywords': ['گردشگری', 'ساحل', 'جزیره', 'تفریح', 'هتل', 'جاذبه', 'مسافرت', 'دیدنی'],
                'weight': 1.0
            },
            'food': {
                'keywords': ['غذا', 'رستوران', 'قلیه', 'خرما', 'ماهی', 'نان', 'چای', 'مهیاوه', 'سوراغ'],
                'weight': 1.0
            },
            'translation': {
                'keywords': ['ترجمه', 'معنی', 'یعنی', 'چی میشه', 'بندری', 'گویش'],
                'weight': 1.1
            },
            'location': {
                'keywords': ['کجاست', 'موقعیت', 'مکان', 'آدرس', 'نشانی', 'محله', 'جا'],
                'weight': 1.0
            },
            'culture': {
                'keywords': ['مراسم', 'عروسی', 'لیوا', 'برکه‌زنی', 'مولودی', 'حنابندان', 'رسوم'],
                'weight': 1.0
            },
            'general': {
                'keywords': ['سلام', 'خداحافظ', 'چطوری', 'ممنون', 'خوبی', 'ابی چش'],
                'weight': 0.8
            }
        }
        self.normalizer = TextNormalizer()
    
    def detect(self, text: str) -> Dict[str, Any]:
        """تشخیص نیت از متن"""
        normalized = self.normalizer.normalize_for_match(text)
        scores = {}
        
        for intent, data in self.intents.items():
            score = 0
            for keyword in data['keywords']:
                if keyword in normalized:
                    score += data['weight']
            if score > 0:
                scores[intent] = score
        
        if not scores:
            return {
                'intent': 'general',
                'confidence': 0.3,
                'alternatives': []
            }
        
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        max_score = sorted_scores[0][1]
        confidence = min(1.0, max_score / 3.0)
        
        return {
            'intent': sorted_scores[0][0],
            'confidence': round(confidence, 2),
            'alternatives': [{'intent': i, 'score': round(s / max_score, 2)} 
                           for i, s in sorted_scores[1:4]]
        }


# ============================================================
# ۳. سیستم RAG با دو دیتابیس
# ============================================================

class DualRAGEngine:
    """سیستم جستجوی دانش با پشتیبانی از دو دیتابیس"""
    
    def __init__(self, bandari_db: str = BANDARI_DB_PATH, hormozgan_db: str = HORMOZGAN_DB_PATH):
        self.bandari_db = bandari_db
        self.hormozgan_db = hormozgan_db
        self.normalizer = TextNormalizer()
        self._cache = {}
        self._cache_ttl = 60
    
    def _get_bandari_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.bandari_db)
    
    def _get_hormozgan_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.hormozgan_db)
    
    def search(self, query: str, dialect: str = 'ban') -> Dict[str, Any]:
        """جستجوی دانش از هر دو دیتابیس"""
        normalized = self.normalizer.normalize_for_match(query)
        
        # بررسی کش
        cache_key = f"{normalized}:{dialect}"
        if cache_key in self._cache:
            cached = self._cache[cache_key]
            if time.time() - cached['time'] < self._cache_ttl:
                return cached['data']
        
        results = []
        
        # ۱. جستجو در دیتابیس بندری (واژگان)
        vocab_results = self._search_bandari_vocabulary(normalized, dialect)
        if vocab_results:
            results.extend(vocab_results)
        
        # ۲. جستجو در دانش محلی بندری
        knowledge_results = self._search_bandari_knowledge(normalized)
        if knowledge_results:
            results.extend(knowledge_results)
        
        # ۳. جستجو در دیتابیس هرمزگان (اطلاعات جغرافیایی)
        geo_results = self._search_hormozgan_data(normalized)
        if geo_results:
            results.extend(geo_results)
        
        # ۴. جستجو در POI های هرمزگان
        poi_results = self._search_hormozgan_poi(normalized)
        if poi_results:
            results.extend(poi_results)
        
        if results:
            response = {
                'found': True,
                'results': results[:10],
                'count': len(results),
                'source': 'dual_database',
                'dialect': dialect,
                'bandari_db': self.bandari_db,
                'hormozgan_db': self.hormozgan_db
            }
            self._cache[cache_key] = {'data': response, 'time': time.time()}
            return response
        
        return {
            'found': False,
            'results': [],
            'count': 0,
            'source': 'none',
            'dialect': dialect
        }
    
    def _search_bandari_vocabulary(self, query: str, dialect: str = 'ban') -> List[Dict]:
        """جستجو در واژگان بندری"""
        try:
            conn = self._get_bandari_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    word_standard,
                    word_bandari,
                    dialect_code,
                    definition,
                    category,
                    subcategory,
                    confidence_score,
                    data_quality,
                    region_usage
                FROM bandari_words
                WHERE dialect_code = ?
                  AND (word_standard LIKE ?
                    OR word_bandari LIKE ?
                    OR definition LIKE ?)
                ORDER BY confidence_score DESC
                LIMIT 5
            """, (dialect, f"%{query}%", f"%{query}%", f"%{query}%"))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [{
                'type': 'vocabulary',
                'source_db': 'bandari',
                'persian': row[0],
                'bandari': row[1],
                'dialect': row[2],
                'definition': row[3] or '',
                'category': row[4] or '',
                'subcategory': row[5] or '',
                'confidence': row[6] or 0.8,
                'quality': row[7] or 'sourced',
                'region': row[8] or ''
            } for row in rows]
            
        except Exception as e:
            return []
    
    def _search_bandari_knowledge(self, query: str) -> List[Dict]:
        """جستجو در دانش محلی بندری"""
        try:
            conn = self._get_bandari_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    title,
                    content,
                    category,
                    region
                FROM local_knowledge
                WHERE title LIKE ?
                   OR content LIKE ?
                   OR category LIKE ?
                   OR region LIKE ?
                LIMIT 5
            """, (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%"))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [{
                'type': 'local_knowledge',
                'source_db': 'bandari',
                'title': row[0],
                'content': row[1],
                'category': row[2] or 'general',
                'region': row[3] or 'همه مناطق'
            } for row in rows]
            
        except Exception as e:
            return []
    
    def _search_hormozgan_data(self, query: str) -> List[Dict]:
        """جستجو در دیتابیس هرمزگان (اطلاعات عمومی)"""
        try:
            conn = self._get_hormozgan_connection()
            cursor = conn.cursor()
            
            # تلاش برای پیدا کردن جدول‌های موجود
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            results = []
            
            # جستجو در جدول‌های مختلف
            for table in tables[:10]:  # محدودیت برای جلوگیری از کندی
                try:
                    cursor.execute(f"""
                        SELECT * FROM {table} 
                        WHERE CAST(rowid AS TEXT) LIKE ? 
                           OR CAST(* AS TEXT) LIKE ?
                        LIMIT 3
                    """, (f"%{query}%", f"%{query}%"))
                    rows = cursor.fetchall()
                    if rows:
                        results.append({
                            'type': 'hormozgan_data',
                            'source_db': 'hormozgan_master',
                            'table': table,
                            'data': [dict(zip([desc[0] for desc in cursor.description], row)) for row in rows[:3]]
                        })
                except:
                    continue
            
            conn.close()
            return results
            
        except Exception as e:
            return []
    
    def _search_hormozgan_poi(self, query: str) -> List[Dict]:
        """جستجو در POI های هرمزگان"""
        try:
            conn = self._get_hormozgan_connection()
            cursor = conn.cursor()
            
            # جستجو در جدول poi ها
            try:
                cursor.execute("""
                    SELECT 
                        name,
                        cat,
                        city,
                        district,
                        lat,
                        lon,
                        address,
                        phone
                    FROM pois
                    WHERE name LIKE ?
                       OR cat LIKE ?
                       OR city LIKE ?
                       OR district LIKE ?
                       OR address LIKE ?
                    LIMIT 5
                """, (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%"))
                
                rows = cursor.fetchall()
                conn.close()
                
                return [{
                    'type': 'poi',
                    'source_db': 'hormozgan_master',
                    'name': row[0],
                    'category': row[1],
                    'city': row[2],
                    'district': row[3],
                    'lat': row[4],
                    'lon': row[5],
                    'address': row[6],
                    'phone': row[7]
                } for row in rows]
                
            except:
                conn.close()
                return []
            
        except Exception as e:
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """آمار هر دو دیتابیس"""
        stats = {
            'bandari_db': {'path': self.bandari_db, 'tables': {}},
            'hormozgan_db': {'path': self.hormozgan_db, 'tables': {}}
        }
        
        # آمار دیتابیس بندری
        try:
            conn = self._get_bandari_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM bandari_words")
            stats['bandari_db']['tables']['bandari_words'] = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM local_knowledge")
            stats['bandari_db']['tables']['local_knowledge'] = cursor.fetchone()[0]
            conn.close()
        except:
            pass
        
        # آمار دیتابیس هرمزگان
        try:
            conn = self._get_hormozgan_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            for table in cursor.fetchall():
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                    stats['hormozgan_db']['tables'][table[0]] = cursor.fetchone()[0]
                except:
                    pass
            conn.close()
        except:
            pass
        
        return stats


# ============================================================
# ۴. موتور اصلی هوش مصنوعی (با دو دیتابیس)
# ============================================================

@dataclass
class AIResponse:
    input_text: str
    intent: str
    confidence: float
    dialect: str
    results: List[Dict]
    translation: Optional[str] = None
    response: str = ""
    elapsed_ms: float = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class HDPAIV6Dual:
    """هوش مصنوعی HDP نسخه ۶ با پشتیبانی از دو دیتابیس"""
    
    def __init__(self, bandari_db: str = BANDARI_DB_PATH, hormozgan_db: str = HORMOZGAN_DB_PATH):
        self.bandari_db = bandari_db
        self.hormozgan_db = hormozgan_db
        self.normalizer = TextNormalizer()
        self.intent_engine = IntentEngine()
        self.rag_engine = DualRAGEngine(bandari_db, hormozgan_db)
        self._history = []
        self._max_history = 50
        
        # بارگذاری دیکشنری از دیتابیس بندری
        self._load_dictionary()
    
    def _load_dictionary(self):
        """بارگذاری دیکشنری در کش"""
        self._dictionary = {}
        try:
            conn = sqlite3.connect(self.bandari_db)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT word_standard, word_bandari, dialect_code, definition 
                FROM bandari_words
            """)
            for row in cursor.fetchall():
                self._dictionary[row[0]] = {
                    'bandari': row[1],
                    'dialect': row[2],
                    'definition': row[3]
                }
            conn.close()
        except Exception:
            pass
    
    def process(self, text: str, dialect: str = 'ban') -> AIResponse:
        """پردازش کامل یک پیام کاربر"""
        start_time = time.time()
        
        # تشخیص گویش
        detected_dialect = self.normalizer.detect_dialect(text)
        if detected_dialect:
            dialect = detected_dialect
        
        # ۱. تشخیص نیت
        intent_result = self.intent_engine.detect(text)
        intent = intent_result['intent']
        confidence = intent_result['confidence']
        
        # ۲. جستجوی RAG از هر دو دیتابیس
        rag_result = self.rag_engine.search(text, dialect)
        
        # ۳. ترجمه
        translation = None
        if intent == 'translation' or confidence > 0.4:
            translation = self._translate(text, dialect)
        
        # ۴. تولید پاسخ
        response = self._generate_response(
            text=text,
            intent=intent,
            confidence=confidence,
            dialect=dialect,
            rag_result=rag_result,
            translation=translation
        )
        
        # ۵. ثبت در تاریخچه
        self._add_history(text, response)
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        return AIResponse(
            input_text=text,
            intent=intent,
            confidence=confidence,
            dialect=dialect,
            results=rag_result.get('results', []),
            translation=translation,
            response=response,
            elapsed_ms=round(elapsed_ms, 2)
        )
    
    def _translate(self, text: str, dialect: str = 'ban') -> Optional[str]:
        """ترجمه به گویش بندری"""
        words = text.split()
        translated = []
        for word in words:
            clean = word.strip('.,!?')
            if clean in self._dictionary:
                entry = self._dictionary[clean]
                translated.append(entry['bandari'])
            else:
                translated.append(clean)
        return ' '.join(translated) if translated != words else None
    
    def _generate_response(self, text: str, intent: str, confidence: float,
                          dialect: str, rag_result: Dict,
                          translation: Optional[str]) -> str:
        """تولید پاسخ بر اساس نتایج"""
        responses = []
        
        # احوالپرسی
        if intent == 'general' or confidence < 0.3:
            return self._get_greeting_response(text, dialect)
        
        # نتایج RAG
        if rag_result.get('found') and rag_result.get('results'):
            responses.append(self._format_results(rag_result['results'][:3], dialect))
        
        # ترجمه
        if translation:
            dialect_name = self.normalizer.dialects.get(dialect, 'بندری')
            responses.append(f"🔤 ترجمه به {dialect_name}: «{translation}»")
        
        # اطلاعات از دیتابیس هرمزگان
        if rag_result.get('source') == 'dual_database':
            responses.append(f"📊 جستجو در: {rag_result.get('bandari_db', '')} و {rag_result.get('hormozgan_db', '')}")
        
        if not responses:
            return self._get_fallback_response(intent, dialect)
        
        return '\n\n'.join(responses[:4])
    
    def _format_results(self, results: List[Dict], dialect: str) -> str:
        """فرمت‌بندی نتایج"""
        formatted = []
        dialect_name = self.normalizer.dialects.get(dialect, 'بندری')
        
        for r in results[:3]:
            if r.get('type') == 'vocabulary':
                formatted.append(
                    f"📖 {r.get('persian', '')} → {r.get('bandari', '')} ({dialect_name})"
                )
            elif r.get('type') == 'local_knowledge':
                formatted.append(
                    f"📚 {r.get('title', '')}: {r.get('content', '')[:80]}..."
                )
            elif r.get('type') == 'poi':
                formatted.append(
                    f"📍 {r.get('name', '')} ({r.get('city', '')})"
                )
            elif r.get('type') == 'hormozgan_data':
                for item in r.get('data', [])[:2]:
                    formatted.append(f"🗺️ {str(item)[:100]}...")
        
        return '\n'.join(formatted) if formatted else ""
    
    def _get_greeting_response(self, text: str, dialect: str) -> str:
        """پاسخ به احوالپرسی"""
        dialect_name = self.normalizer.dialects.get(dialect, 'بندری')
        
        if 'سلام' in text:
            return f"سَلام! خوش آمدید به سرویس هوشمند {dialect_name}. چطور می‌توانم کمک کنم؟"
        elif 'چطوری' in text or 'خوبی' in text:
            return "خوبم، ممنون! شما چطورید؟"
        elif 'خداحافظ' in text:
            return "خدا نگهدار! بازم سر بزنید."
        elif 'ممنون' in text:
            return "خواهش می‌کنم! خوشحالم که کمک کردم."
        else:
            return f"سلام! من هوش مصنوعی گویش {dialect_name} هستم. چگونه می‌توانم به شما کمک کنم؟"
    
    def _get_fallback_response(self, intent: str, dialect: str) -> str:
        """پاسخ پیش‌فرض"""
        fallbacks = {
            'traffic': "اطلاعات ترافیک را از دیتابیس هرمزگان بررسی می‌کنم. لطفاً دقیق‌تر بپرسید.",
            'health': "برای یافتن مراکز درمانی در حال جستجو در دیتابیس هرمزگان هستم.",
            'tourism': "جاذبه‌های گردشگری هرمزگان بسیار زیاد است. کدام منطقه مد نظر شماست؟",
            'food': "غذاهای محلی هرمزگان متنوع هستند. چه نوع غذایی دوست دارید؟",
            'translation': f"برای ترجمه به گویش {self.normalizer.dialects.get(dialect, 'بندری')}، کلمه یا جمله را بفرمایید.",
            'location': "برای پیدا کردن مکان، از دیتابیس هرمزگان جستجو می‌کنم.",
        }
        return fallbacks.get(intent, "در حال جستجو در هر دو دیتابیس هستم. کمی صبر کنید...")
    
    def _add_history(self, text: str, response: str):
        self._history.append({
            'text': text,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]
    
    def get_history(self, limit: int = 10) -> List[Dict]:
        return self._history[-limit:]
    
    def get_stats(self) -> Dict[str, Any]:
        rag_stats = self.rag_engine.get_stats()
        return {
            'version': '6.0.0-dual',
            'bandari_db': self.bandari_db,
            'hormozgan_db': self.hormozgan_db,
            'history_size': len(self._history),
            'dictionary_size': len(self._dictionary),
            'intents': list(self.intent_engine.intents.keys()),
            'rag_stats': rag_stats,
            'dialects': list(self.normalizer.dialects.keys())
        }


# ============================================================
# ۵. رابط خط فرمان
# ============================================================

def main():
    """رابط خط فرمان"""
    print("=" * 70)
    print("🌊 HDP AI v6.0 - Dual Database Bandari Dialect AI System")
    print("=" * 70)
    print(f"📁 دیتابیس بندری: {BANDARI_DB_PATH}")
    print(f"📁 دیتابیس هرمزگان: {HORMOZGAN_DB_PATH}")
    print()
    
    ai = HDPAIV6Dual()
    stats = ai.get_stats()
    
    print(f"📊 آمار سیستم:")
    print(f"   - نسخه: {stats['version']}")
    print(f"   - تعداد واژگان بندری: {stats['dictionary_size']}")
    print(f"   - گویش‌ها: {', '.join(stats['dialects'])}")
    print(f"   - دیتابیس هرمزگان: {list(stats['rag_stats']['hormozgan_db']['tables'].keys())[:5]}...")
    print()
    
    print("💬 برای شروع تایپ کنید (برای خروج exit)")
    print("-" * 70)
    
    while True:
        try:
            user_input = input("\n👤 شما: ").strip()
            if user_input.lower() in ['exit', 'quit', 'خروج']:
                print("👋 خداحافظ! خدا نگهدار!")
                break
            
            if not user_input:
                continue
            
            response = ai.process(user_input)
            
            print(f"\n🤖 پاسخ:")
            print(f"   📌 نیت: {response.intent} (اعتماد: {response.confidence})")
            print(f"   🗣️ گویش: {response.dialect}")
            if response.translation:
                print(f"   🔤 ترجمه: {response.translation}")
            if response.results:
                print(f"   📚 نتایج: {len(response.results)} مورد")
            print(f"\n📝 {response.response}")
            print(f"\n⏱️ {response.elapsed_ms:.2f} ms")
            
        except KeyboardInterrupt:
            print("\n👋 خداحافظ!")
            break
        except Exception as e:
            print(f"❌ خطا: {e}")


if __name__ == "__main__":
    main()
