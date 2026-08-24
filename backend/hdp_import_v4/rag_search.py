#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import sys

class RAGSearch:
    def __init__(self, db_path="hdp_knowledge.db"):
        """اتصال به پایگاه داده"""
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
    
    def search_by_category(self, category, limit=20):
        """جستجو بر اساس دسته‌بندی"""
        sql = """
        SELECT 
            table_name,
            title,
            content,
            location,
            category
        FROM rag_fts
        WHERE category = ?
        LIMIT ?
        """
        cursor = self.conn.execute(sql, (category, limit))
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
        """بستن اتصال"""
        self.conn.close()

# ============================================================
# استفاده مستقیم از خط فرمان
# ============================================================
if __name__ == "__main__":
    rag = RAGSearch()
    
    if len(sys.argv) > 1:
        query = sys.argv[1]
        category = sys.argv[2] if len(sys.argv) > 2 else None
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 10
        
        print(f"\n🔍 جستجوی: {query}")
        if category:
            print(f"📂 دسته‌بندی: {category}")
        print("-" * 50)
        
        results = rag.search(query, category, limit)
        
        if results:
            for i, row in enumerate(results, 1):
                print(f"{i}. [{row['category']}] {row['title']}")
                print(f"   📍 {row['location']}")
                print(f"   📝 {row['content'][:100]}...")
                print(f"   ⭐ امتیاز: {row['rank']:.2f}")
                print()
        else:
            print("❌ نتیجه‌ای یافت نشد!")
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
            print(f"  - {cat['category']}: {cat['count']} مورد")
        
        print("\n💡 مثال:")
        print("  python3 rag_search.py 'بیمارستان'")
        print("  python3 rag_search.py 'کودکان' 'بیمارستان'")
        print("  python3 rag_search.py 'مرکز خرید' 'مرکز خرید' 5")
    
    rag.close()
