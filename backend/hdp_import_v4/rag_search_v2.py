#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import sys

class RAGSearch:
    def __init__(self, db_path="hdp_knowledge.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
    
    def search(self, query, category=None, limit=10):
        """جستجو در سیستم RAG"""
        sql = """
        SELECT 
            table_name,
            title,
            content,
            location,
            category,
            rank
        FROM rag_fts
        WHERE rag_fts MATCH ?
        """
        params = [query]
        
        if category:
            sql += " AND category = ?"
            params.append(category)
        
        sql += " ORDER BY rank LIMIT ?"
        params.append(limit)
        
        cursor = self.conn.execute(sql, params)
        results = cursor.fetchall()
        return [dict(row) for row in results]
    
    def search_all(self, query, limit=20):
        """جستجو در همه دسته‌بندی‌ها"""
        sql = """
        SELECT 
            table_name,
            title,
            content,
            location,
            category,
            rank
        FROM rag_fts
        WHERE rag_fts MATCH ?
        ORDER BY rank
        LIMIT ?
        """
        cursor = self.conn.execute(sql, (query, limit))
        results = cursor.fetchall()
        return [dict(row) for row in results]
    
    def get_categories(self):
        """دریافت لیست همه دسته‌بندی‌ها"""
        sql = """
        SELECT category, COUNT(*) as count
        FROM rag_fts
        GROUP BY category
        ORDER BY count DESC
        """
        cursor = self.conn.execute(sql)
        results = cursor.fetchall()
        return [dict(row) for row in results]
    
    def close(self):
        self.conn.close()

# ============================================================
# نگاشت دسته‌بندی‌ها به نام‌های قابل فهم
# ============================================================
CATEGORY_MAP = {
    'محله': '🏘️ محلات',
    'درمانگاه': '🏥 مراکز درمانی',
    'اسکله و بندر': '⚓ اسکله و بندر',
    'ورزش': '⚽ مراکز ورزشی',
    'منطقه شهری': '🗺️ مناطق شهری',
    'مرکز خرید': '🛍️ مراکز خرید',
    'پارک و تفریح': '🌳 پارک و تفریح',
    'دانشگاه': '🎓 دانشگاه‌ها',
    'صنعت': '🏭 صنایع',
    'مکان مذهبی': '🕌 اماکن مذهبی',
    'هتل': '🏨 هتل‌ها',
    'حمل و نقل': '🚌 حمل و نقل',
    'اداره': '🏛️ ادارات',
    'اطلاعات شهری': '📊 اطلاعات شهری',
    'تاریخچه': '📜 تاریخچه',
}

def get_category_label(category):
    return CATEGORY_MAP.get(category, category)

if __name__ == "__main__":
    rag = RAGSearch()
    
    if len(sys.argv) > 1:
        query = sys.argv[1]
        category = sys.argv[2] if len(sys.argv) > 2 else None
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 10
        
        print(f"\n🔍 جستجوی: {query}")
        if category:
            print(f"📂 دسته‌بندی: {get_category_label(category)}")
        print("-" * 50)
        
        # جستجو در همه دسته‌بندی‌ها اگر دسته‌بندی مشخص نشده باشد
        if category:
            results = rag.search(query, category, limit)
        else:
            results = rag.search_all(query, limit)
        
        if results:
            for i, row in enumerate(results, 1):
                cat_label = get_category_label(row['category'])
                print(f"{i}. [{cat_label}] {row['title']}")
                if row['location'] and row['location'] != 'None':
                    print(f"   📍 {row['location']}")
                if row['content'] and row['content'] != 'None':
                    print(f"   📝 {row['content'][:100]}...")
                if 'rank' in row:
                    print(f"   ⭐ امتیاز: {row['rank']:.2f}")
                print()
            
            print(f"✅ {len(results)} نتیجه یافت شد")
        else:
            print("❌ نتیجه‌ای یافت نشد!")
            
            # پیشنهاد دسته‌بندی‌های مشابه
            print("\n💡 دسته‌بندی‌های موجود:")
            categories = rag.get_categories()
            for cat in categories:
                cat_label = get_category_label(cat['category'])
                print(f"  - {cat_label}: {cat['count']} مورد")
    else:
        # نمایش راهنما
        print("=" * 50)
        print("🤖 سیستم جستجوی RAG - بندرعباس")
        print("=" * 50)
        
        print("\n📌 دستورات:")
        print("  python3 rag_search.py 'کلمه جستجو'")
        print("  python3 rag_search.py 'کلمه جستجو' 'دسته‌بندی'")
        print("  python3 rag_search.py 'کلمه جستجو' 'دسته‌بندی' تعداد")
        
        print("\n📂 دسته‌بندی‌های موجود:")
        categories = rag.get_categories()
        for cat in categories:
            cat_label = get_category_label(cat['category'])
            print(f"  - {cat_label}: {cat['count']} مورد")
        
        print("\n💡 مثال‌ها:")
        print("  python3 rag_search.py 'کودکان'")
        print("  python3 rag_search.py 'بیمارستان' 'درمانگاه'")
        print("  python3 rag_search.py 'مرکز خرید' 'مرکز خرید' 5")
        print("  python3 rag_search.py 'پارک' 'پارک و تفریح'")
    
    rag.close()
