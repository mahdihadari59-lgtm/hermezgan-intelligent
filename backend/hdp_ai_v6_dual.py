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
    
    def process(self, text: str):
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
        results = self._search_hormozgan(text)
        
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
    
    def _search_hormozgan(self, text: str) -> List[Dict]:
        """جستجو در دیتابیس هرمزگان"""
        results = []
        if not os.path.exists(self.hormozgan_db):
            return results
        
        try:
            conn = sqlite3.connect(self.hormozgan_db)
            cursor = conn.cursor()
            
            # جستجو در جدول pois
            try:
                cursor.execute("""
                    SELECT name, cat, city, district, address 
                    FROM pois 
                    WHERE name LIKE ? OR cat LIKE ? OR city LIKE ?
                    LIMIT 5
                """, (f"%{text}%", f"%{text}%", f"%{text}%"))
                
                for row in cursor.fetchall():
                    results.append({
                        'type': 'poi',
                        'name': row[0] or 'نامشخص',
                        'category': row[1] or 'عمومی',
                        'city': row[2] or 'نامشخص',
                        'district': row[3] or '',
                        'address': row[4] or ''
                    })
            except:
                pass
            
            conn.close()
        except Exception as e:
            print(f"⚠️ خطا در جستجوی هرمزگان: {e}")
        
        return results
    
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
