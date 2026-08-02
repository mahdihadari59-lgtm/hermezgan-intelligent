"""
Knowledge Base - جستجوی هوشمند در تمام جداول
"""

import sqlite3
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


class KnowledgeBase:
    """مدیریت دانش با جستجو در تمام جداول مرتبط"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        self._initialized = True
        self.db_path = Path("/data/data/com.termux/files/home/hermezgan-intelligent-backup-20260729/backend/hdp_v2.db")
        self._conn = None
        self._connect()
        self._table_priority = self._get_table_priority()
        logger.info(f"✅ Knowledge Base initialized with {len(self._table_priority)} priority tables")

    def _connect(self):
        """اتصال به دیتابیس"""
        try:
            if not self.db_path.exists():
                logger.error(f"❌ Database not found: {self.db_path}")
                return
            
            self._conn = sqlite3.connect(str(self.db_path))
            self._conn.row_factory = sqlite3.Row
            logger.info(f"✅ Connected to database: {self.db_path}")
        except Exception as e:
            logger.error(f"❌ Connection error: {e}")
            self._conn = None

    def _get_table_priority(self) -> Dict[str, int]:
        """اولویت جداول برای جستجو"""
        return {
            # اولویت ۱: دانش اصلی
            'knowledge': 100,
            'knowledge_aliases': 90,
            'knowledge_categories': 85,
            
            # اولویت ۲: مکان‌ها و جاذبه‌ها
            'places': 80,
            'cities': 80,
            'attractions': 75,
            'hotels': 75,
            'restaurants': 75,
            
            # اولویت ۳: خدمات شهری
            'hospitals': 70,
            'schools': 70,
            'police_stations': 70,
            'fuel_stations': 65,
            
            # اولویت ۴: ترافیک و حمل و نقل
            'traffic_cameras': 60,
            'traffic_accidents': 60,
            'traffic_blackspots': 60,
            
            # اولویت ۵: گراف دانش
            'knowledge_graph': 50,
            'knowledge_nodes': 50,
            'knowledge_edges': 50,
            
            # اولویت ۶: اطلس و فرهنگ
            'atlas_master': 40,
            'cultural_items': 40,
            'proverbs': 40,
            
            # اولویت ۷: مکالمات و گویش
            'dialect_terms': 30,
            'conversation_context': 30,
        }

    def _get_table_schema(self, table_name: str) -> List[str]:
        """دریافت اسکیما و ستون‌های متنی یک جدول"""
        try:
            cursor = self._conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            text_columns = []
            for col in columns:
                col_name = col[1]
                col_type = col[2].lower()
                if 'text' in col_type or 'varchar' in col_type or col_name in ['content', 'answer', 'title', 'name', 'description']:
                    text_columns.append(col_name)
            return text_columns
        except Exception as e:
            logger.debug(f"⚠️ Schema error for {table_name}: {e}")
            return []

    def _search_table(self, table_name: str, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """جستجو در یک جدول خاص"""
        results = []
        try:
            text_columns = self._get_table_schema(table_name)
            if not text_columns:
                return results

            cursor = self._conn.cursor()
            search_term = f"%{query}%"
            
            # ساخت شرط جستجو
            conditions = " OR ".join([f"{col} LIKE ?" for col in text_columns])
            sql = f"SELECT * FROM {table_name} WHERE {conditions} LIMIT ?"
            params = [search_term] * len(text_columns) + [limit]
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            for row in rows:
                row_dict = dict(row)
                # پیدا کردن بهترین محتوا
                content = None
                for key in ['content', 'answer', 'text', 'description', 'name', 'title']:
                    if key in row_dict and row_dict[key]:
                        content = row_dict[key]
                        break
                
                if content:
                    results.append({
                        "table": table_name,
                        "content": content,
                        "title": row_dict.get('title', row_dict.get('name', '')),
                        "category": row_dict.get('category', 'general'),
                        "city": row_dict.get('city', ''),
                        "score": 0,  # بعداً محاسبه میشه
                        "metadata": row_dict
                    })
            
        except Exception as e:
            logger.debug(f"⚠️ Search error in {table_name}: {e}")
        
        return results

    def search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """جستجوی ترکیبی در همه جداول با اولویت"""
        if self._conn is None:
            return []
        
        all_results = []
        query_lower = query.lower()
        
        # جستجو در جداول با اولویت
        for table, priority in sorted(self._table_priority.items(), key=lambda x: -x[1]):
            try:
                # امتحان کردن تعداد نتایج مختلف
                for limit in [3, 2, 1]:
                    results = self._search_table(table, query, limit=limit)
                    if results:
                        for r in results:
                            # محاسبه امتیاز نهایی
                            r['_score'] = self._calculate_score(r, query_lower, priority)
                            all_results.append(r)
                        break  # اگر نتیجه پیدا شد، ادامه نده
            except Exception as e:
                logger.debug(f"⚠️ Error searching {table}: {e}")
        
        # مرتب‌سازی بر اساس امتیاز
        all_results.sort(key=lambda x: x.get('_score', 0), reverse=True)
        
        return all_results[:top_k]

    def _calculate_score(self, result: Dict[str, Any], query: str, table_priority: int) -> float:
        """محاسبه امتیاز نهایی یک نتیجه"""
        score = 0.0
        
        content = result.get('content', '').lower()
        title = result.get('title', '').lower()
        
        # ۱. تطابق کامل عبارت (۵۰ امتیاز)
        if query in content:
            score += 50
        if query in title:
            score += 30
        
        # ۲. تطابق کلمات (۲۰ امتیاز)
        query_words = query.split()
        for word in query_words:
            if len(word) > 2:
                if word in content:
                    score += 10
                if word in title:
                    score += 5
        
        # ۳. اولویت جدول (۲۰ امتیاز)
        score += (table_priority / 100) * 20
        
        # ۴. امتیاز دسته‌بندی (۱۰ امتیاز)
        category = result.get('category', '')
        if category in ['tourism', 'location', 'knowledge', 'food', 'health']:
            score += 10
        
        # ۵. امتیاز شهر (۵ امتیاز)
        city = result.get('city', '')
        if city and city in query:
            score += 5
        
        return min(score, 100)

    def get_best_answer(self, query: str) -> Optional[Dict[str, Any]]:
        """دریافت بهترین پاسخ"""
        results = self.search(query, top_k=5)
        if results:
            best = results[0]
            return {
                "answer": best.get('content', ''),
                "title": best.get('title', ''),
                "category": best.get('category', 'general'),
                "score": best.get('_score', 0),
                "source": best.get('table', 'database'),
                "metadata": best.get('metadata', {}),
                "documents": results[:3]
            }
        return None

    def get_stats(self) -> Dict[str, Any]:
        """آمار دیتابیس"""
        if self._conn is None:
            return {"error": "No connection"}
        
        stats = {}
        try:
            cursor = self._conn.cursor()
            for table in self._table_priority.keys():
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    stats[table] = count
                except:
                    pass
            return stats
        except Exception as e:
            return {"error": str(e)}


def get_knowledge_base():
    return KnowledgeBase()
