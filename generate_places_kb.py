#!/usr/bin/env python3
"""
Generate Bandar Abbas Places Knowledge Base
Creates comprehensive knowledge base with categories, descriptions, and search index
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List
from datetime import datetime

class PlacesKnowledgeBaseGenerator:
    def __init__(self, db_path: str = "geo.db", json_path: str = "bandar_places.json"):
        self.db_path = db_path
        self.json_path = json_path
        self.conn = None
        
        self.category_descriptions = {
            "cafe": {
                "name": "کافه‌ها و چایخانه‌ها",
                "icon": "☕",
                "emoji": "☕",
                "description": "کافه‌ها، چایخانه‌ها و قهوه‌فروشی‌های بندرعباس از مراکز مهم اجتماعی و فرهنگی شهر هستند. از کافه‌های مدرن تا چایخانه‌های سنتی، هر کدام فضایی منحصربه‌فرد برای گذراندن اوقات فراغت ارائه می‌دهند.",
                "keywords": ["قهوه", "چای", "نوشیدنی", "استراحت", "گفتگو"]
            },
            "restaurant": {
                "name": "رستوران‌ها و غذاخوری‌ها",
                "icon": "🍽️",
                "emoji": "🍽️",
                "description": "بندرعباس با تنوع غذایی بالا، میزبان رستوران‌های دریایی، سنتی، فست‌فود و بین‌المللی است. غذاهای دریایی تازه مهم‌ترین ویژگی رستوران‌های این شهر بندری است.",
                "keywords": ["غذا", "غذاخوری", "ناهار", "شام", "دریایی", "سنتی"]
            },
            "hotel": {
                "name": "هتل‌ها و اقامتگاه‌ها",
                "icon": "🏨",
                "emoji": "🏨",
                "description": "از هتل‌های لوکس ۵ ستاره تا اقامتگاه‌های اقتصادی و بوم‌گردی، بندرعباس گزینه‌های متنوعی برای اقامت مسافران فراهم کرده است.",
                "keywords": ["هتل", "اقامت", "مسافران", "اتاق", "رزرو", "بوم‌گردی"]
            },
            "hospital": {
                "name": "بیمارستان‌ها و مراکز درمانی",
                "icon": "🏥",
                "emoji": "🏥",
                "description": "بندرعباس دارای بیمارستان‌های مجهز دولتی و خصوصی از جمله بیمارستان شهید محمدی، بیمارستان کودکان و بیمارستان خلیج فارس است که خدمات درمانی به سراسر استان ارائه می‌دهند.",
                "keywords": ["بیمارستان", "پزشک", "درمان", "فوریت", "آمبولانس"]
            },
            "pharmacy": {
                "name": "داروخانه‌ها",
                "icon": "💊",
                "emoji": "💊",
                "description": "داروخانه‌های شبانه‌روزی و روزانه در سراسر شهر پراکنده‌اند و دسترسی به دارو را برای شهروندان آسان کرده‌اند.",
                "keywords": ["داروخانه", "دارو", "شبانه‌روزی", "نسخه"]
            },
            "bank": {
                "name": "بانک‌ها و مؤسسات مالی",
                "icon": "🏦",
                "emoji": "🏦",
                "description": "تمامی بانک‌های دولتی و خصوصی ایران در بندرعباس شعبه دارند. مرکز مالی استان با دسترسی آسان به خدمات بانکی.",
                "keywords": ["بانک", "حساب", "شعبه", "تراکنش", "صحاف"]
            },
            "fuel": {
                "name": "پمپ بنزین‌ها و جایگاه‌های سوخت",
                "icon": "⛽",
                "emoji": "⛽",
                "description": "جایگاه‌های بنزین، گازوئیل و CNG در سراسر بندرعباس و جاده‌های اطراف پراکنده‌اند. برخی جایگاه‌ها ۲۴ ساعته فعال هستند.",
                "keywords": ["بنزین", "گازوئیل", "CNG", "سوخت", "پمپ"]
            },
            "school": {
                "name": "مدارس و مراکز آموزشی",
                "icon": "🏫",
                "emoji": "🏫",
                "description": "بندرعباس میزبان مدارس دولتی، غیرانتفاعی، تیزهوشان و هنرستان‌های فنی است. دانشگاه هرمزگان نیز از مراکز آموزش عالی مهم استان است.",
                "keywords": ["مدرسه", "دانشگاه", "آموزش", "تحصیل", "دانشجو"]
            },
            "police": {
                "name": "کلانتری‌ها و مراکز پلیس",
                "icon": "👮",
                "emoji": "👮",
                "description": "مراکز پلیس راهور، کلانتری‌ها و پاسگاه‌های بندرعباس امنیت شهر را تأمین می‌کنند. پلیس راهنمایی و رانندگی نیز در مرکز شهر مستقر است.",
                "keywords": ["پلیس", "کلانتری", "امنیت", "راهور", "پاسگاه"]
            },
            "park": {
                "name": "پارک‌ها و بوستان‌ها",
                "icon": "🌳",
                "emoji": "🌳",
                "description": "بندرعباس دارای پارک‌های متعدد شهری، جنگلی و ساحلی است. پارک جنگلی خلیج فارس، بوستان بانوان و پارک جهانگردی از معروف‌ترین آنها هستند.",
                "keywords": ["پارک", "بوستان", "فضای سبز", "تفریح", "جنگلی"]
            },
            "market": {
                "name": "بازارها و مراکز خرید",
                "icon": "🛍️",
                "emoji": "🛍️",
                "description": "از بازار سنتی بندرعباس تا مراکز خرید مدرن مانند سیتی سنتر، بازار ترک‌ها و بازار ماهی فروشان، این شهر بهشت خریداران است.",
                "keywords": ["بازار", "خرید", "مرکز خرید", "سوق", "کالا"]
            },
            "mosque": {
                "name": "مساجد و اماکن مذهبی",
                "icon": "🕌",
                "emoji": "🕌",
                "description": "مساجد تاریخی و مدرن بندرعباس از جمله مسجد جامع، مسجد ناصری، مسجد صحراباغی و امامزاده سید مظفر از مراکز مهم مذهبی شهر هستند.",
                "keywords": ["مسجد", "نماز", "دین", "امامزاده", "مذهب"]
            },
            "parking": {
                "name": "پارکینگ‌ها",
                "icon": "🅿️",
                "emoji": "🅿️",
                "description": "پارکینگ‌های عمومی و طبقاتی در مرکز شهر، اطراف بازار و فرودگاه بندرعباس دسترسی آسان به خودرو را فراهم می‌کنند.",
                "keywords": ["پارکینگ", "پارک", "خودرو", "طبقاتی"]
            },
            "bus_station": {
                "name": "پایانه‌های مسافربری و ایستگاه‌ها",
                "icon": "🚌",
                "emoji": "🚌",
                "description": "پایانه مسافربری خلیج فارس و ایستگاه‌های اتوبوس شهری، حمل‌ونقل عمومی بندرعباس را تشکیل می‌دهند.",
                "keywords": ["پایانه", "اتوبوس", "حمل‌ونقل", "سفر"]
            },
            "atm": {
                "name": "خودپردازها",
                "icon": "💰",
                "emoji": "💰",
                "description": "دستگاه‌های خودپرداز در سراسر شهر پراکنده‌اند و دسترسی ۲۴ ساعته به پول نقد را فراهم می‌کنند.",
                "keywords": ["خودپرداز", "پول", "نقد", "بانک", "عابر"]
            }
        }

    def connect(self):
        """Connect to database."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self.conn

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()

    def load_places_json(self) -> Dict:
        """Load places from JSON file."""
        with open(self.json_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def generate_knowledge_base(self) -> Dict:
        """Generate comprehensive knowledge base from database."""
        cursor = self.conn.cursor()
        
        kb = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "city": "بندرعباس",
                "region": "هرمزگان",
                "total_places": 0
            },
            "categories": {}
        }
        
        # Get all places grouped by category
        cursor.execute('''
            SELECT category, category_name, COUNT(*) as count
            FROM places
            GROUP BY category, category_name
            ORDER BY count DESC
        ''')
        
        for row in cursor.fetchall():
            category = row['category']
            cat_name = row['category_name']
            count = row['count']
            
            # Get category description
            cat_desc = self.category_descriptions.get(category, {})
            
            kb["categories"][category] = {
                "name": cat_name,
                "display_name": cat_desc.get('name', cat_name),
                "icon": cat_desc.get('icon', '📍'),
                "emoji": cat_desc.get('emoji', '📍'),
                "description": cat_desc.get('description', ''),
                "keywords": cat_desc.get('keywords', []),
                "count": count,
                "places": []
            }
            
            kb["metadata"]["total_places"] += count
            
            # Get places in this category
            cursor.execute('''
                SELECT id, name, lat, lng, icon, tags_json
                FROM places
                WHERE category = ?
                ORDER BY name
            ''', (category,))
            
            for place_row in cursor.fetchall():
                place_data = {
                    "id": place_row['id'],
                    "name": place_row['name'],
                    "lat": place_row['lat'],
                    "lng": place_row['lng'],
                    "icon": place_row['icon']
                }
                
                if place_row['tags_json']:
                    try:
                        place_data["tags"] = json.loads(place_row['tags_json'])
                    except:
                        pass
                
                kb["categories"][category]["places"].append(place_data)
        
        return kb

    def save_knowledge_base(self, kb: Dict, output_path: str):
        """Save knowledge base to JSON file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(kb, f, ensure_ascii=False, indent=2)
        print(f"✓ Knowledge base saved to {output_path}")

    def create_search_index(self) -> Dict:
        """Create search index for fast lookups."""
        cursor = self.conn.cursor()
        
        search_index = {
            "by_name": {},
            "by_category": {},
            "by_location": {},
            "keywords": {}
        }
        
        # Index by name
        cursor.execute('''
            SELECT id, name, category_name, lat, lng, icon
            FROM places
            ORDER BY name
        ''')
        
        for row in cursor.fetchall():
            name_lower = row['name'].lower()
            search_index["by_name"][name_lower] = {
                "id": row['id'],
                "name": row['name'],
                "category": row['category_name'],
                "lat": row['lat'],
                "lng": row['lng'],
                "icon": row['icon']
            }
        
        # Index by category
        cursor.execute('''
            SELECT category_name, COUNT(*) as count
            FROM places
            GROUP BY category_name
        ''')
        
        for row in cursor.fetchall():
            search_index["by_category"][row['category_name']] = row['count']
        
        # Create keywords index
        for category, desc in self.category_descriptions.items():
            for keyword in desc.get('keywords', []):
                if keyword not in search_index["keywords"]:
                    search_index["keywords"][keyword] = []
                search_index["keywords"][keyword].append(category)
        
        return search_index

    def save_search_index(self, search_index: Dict, output_path: str):
        """Save search index to JSON file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(search_index, f, ensure_ascii=False, indent=2)
        print(f"✓ Search index saved to {output_path}")

    def print_statistics(self, kb: Dict):
        """Print knowledge base statistics."""
        print("\n" + "="*70)
        print("📚 BANDAR ABBAS PLACES KNOWLEDGE BASE")
        print("="*70)
        
        print(f"\n📊 Total Places: {kb['metadata']['total_places']}")
        print(f"📅 Generated: {kb['metadata']['generated_at']}")
        
        print("\n🗂️  Categories:")
        print("-" * 70)
        
        for cat_key in sorted(kb["categories"].keys(), 
                             key=lambda x: kb["categories"][x]["count"], 
                             reverse=True):
            cat = kb["categories"][cat_key]
            print(f"  {cat['emoji']} {cat['name']:35} → {cat['count']:4} places")
        
        print("\n" + "="*70 + "\n")

    def run(self):
        """Execute knowledge base generation."""
        try:
            print("🗄️  PLACES KNOWLEDGE BASE GENERATOR")
            print("="*70)
            
            # Connect
            print("\n1️⃣  Connecting to database...")
            self.connect()
            print(f"✓ Connected to {self.db_path}")
            
            # Generate
            print("\n2️⃣  Generating knowledge base...")
            kb = self.generate_knowledge_base()
            
            # Print stats
            self.print_statistics(kb)
            
            # Save KB
            print("\n3️⃣  Saving knowledge base...")
            kb_path = "bandar_places_knowledge.json"
            self.save_knowledge_base(kb, kb_path)
            
            # Create search index
            print("\n4️⃣  Creating search index...")
            search_index = self.create_search_index()
            
            # Save index
            print("\n5️⃣  Saving search index...")
            index_path = "bandar_places_search_index.json"
            self.save_search_index(search_index, index_path)
            
            print("\n✅ KNOWLEDGE BASE GENERATION COMPLETED!")
            print(f"\nGenerated files:")
            print(f"  📄 {kb_path}")
            print(f"  🔍 {index_path}")
            
            return True
            
        except Exception as e:
            print(f"\n❌ GENERATION FAILED: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            self.close()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate Bandar Abbas places knowledge base'
    )
    parser.add_argument(
        '--db',
        default='geo.db',
        help='Path to geo.db database'
    )
    
    args = parser.parse_args()
    
    generator = PlacesKnowledgeBaseGenerator(args.db)
    success = generator.run()
    return 0 if success else 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
