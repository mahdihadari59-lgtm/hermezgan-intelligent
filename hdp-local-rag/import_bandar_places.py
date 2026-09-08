#!/usr/bin/env python3
"""
Import 677 Bandar Abbas places into geo.db
Populates POIs with comprehensive location data and categories
"""

import json
import sqlite3
import sys
from pathlib import Path
from typing import Dict, List, Optional

class BandarAbbasPlacesImporter:
    def __init__(self, db_path: str = "geo.db"):
        self.db_path = db_path
        self.conn = None
        self.place_categories = {
            "cafe": {
                "display_name": "کافه‌ها و چایخانه‌ها",
                "icon": "☕",
                "description": "کافه‌ها، چایخانه‌ها و قهوه‌فروشی‌های بندرعباس از مراکز مهم اجتماعی و فرهنگی شهر هستند."
            },
            "restaurant": {
                "display_name": "رستوران‌ها و غذاخوری‌ها",
                "icon": "🍽️",
                "description": "بندرع��اس با تنوع غذایی بالا، میزبان رستوران‌های دریایی، سنتی، فست‌فود و بین‌المللی است."
            },
            "hotel": {
                "display_name": "هتل‌ها و اقامتگاه‌ها",
                "icon": "🏨",
                "description": "از هتل‌های لوکس ۵ ستاره تا اقامتگاه‌های اقتصادی و بوم‌گردی."
            },
            "hospital": {
                "display_name": "بیمارستان‌ها و مراکز درمانی",
                "icon": "🏥",
                "description": "بیمارستان‌های مجهز دولتی و خصوصی که خدمات درمانی به سراسر استان ارائه می‌دهند."
            },
            "pharmacy": {
                "display_name": "داروخانه‌ها",
                "icon": "💊",
                "description": "داروخانه‌های شبانه‌روزی و روزانه در سراسر شهر."
            },
            "bank": {
                "display_name": "بانک‌ها و مؤسسات مالی",
                "icon": "🏦",
                "description": "تمامی بانک‌های دولتی و خصوصی ایران در بندرعباس شعبه دارند."
            },
            "fuel": {
                "display_name": "پمپ بنزین‌ها و جایگاه‌های سوخت",
                "icon": "⛽",
                "description": "جایگاه‌های بنزین، گازوئیل و CNG در سراسر شهر و جاده‌های اطراف."
            },
            "school": {
                "display_name": "مدارس و مراکز آموزشی",
                "icon": "🏫",
                "description": "مدارس دولتی، غیرانتفاعی، تیزهوشان و هنرستان‌های فنی."
            },
            "police": {
                "display_name": "کلانتری‌ها و مراکز پلیس",
                "icon": "👮",
                "description": "مراکز پلیس راهور، کلانتری‌ها و پاسگاه‌های امنیتی."
            },
            "park": {
                "display_name": "پارک‌ها و بوستان‌ها",
                "icon": "🌳",
                "description": "پارک‌های متعدد شهری، جنگلی و ساحلی."
            },
            "market": {
                "display_name": "بازارها و مراکز خرید",
                "icon": "🛍️",
                "description": "از بازار سنتی تا مراکز خرید مدرن."
            },
            "mosque": {
                "display_name": "مساجد و اماکن مذهبی",
                "icon": "🕌",
                "description": "مساجد تاریخی و مدرن از مراکز مهم مذهبی شهر."
            },
            "parking": {
                "display_name": "پارکینگ‌ها",
                "icon": "🅿️",
                "description": "پارکینگ‌های عمومی و طبقاتی در مرکز شهر."
            },
            "bus_station": {
                "display_name": "پایانه‌های مسافربری و ایستگاه‌ها",
                "icon": "🚌",
                "description": "پایانه مسافربری و ایستگاه‌های اتوبوس شهری."
            },
            "atm": {
                "display_name": "خودپردازها",
                "icon": "💰",
                "description": "دستگاه‌های خودپرداز در سراسر شهر."
            }
        }

    def connect(self):
        """Connect to the database."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self.conn

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()

    def load_places(self, json_path: str) -> Dict:
        """Load Bandar Abbas places JSON file."""
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def create_places_table(self):
        """Create places table if it doesn't exist."""
        cursor = self.conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS places (
                id              INTEGER PRIMARY KEY,
                name            TEXT NOT NULL,
                category        TEXT NOT NULL,
                category_name   TEXT,
                lat             REAL NOT NULL,
                lng             REAL NOT NULL,
                description     TEXT,
                icon            TEXT,
                city            TEXT DEFAULT 'بندرعباس',
                tags_json       TEXT,
                rating          REAL,
                phone           TEXT,
                address         TEXT,
                hours           TEXT,
                website         TEXT,
                tenant_uuid     TEXT DEFAULT 'bandar_abbas',
                updated_at      INTEGER NOT NULL DEFAULT (strftime('%s','now'))
            )
        ''')

        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_places_category ON places(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_places_name ON places(name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_places_city ON places(city)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_places_latlng ON places(lat, lng)')

        # Create R-Tree for spatial queries
        cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS places_rtree USING rtree(
                id, min_lat, max_lat, min_lng, max_lng
            )
        ''')

        # Create triggers for R-Tree sync
        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS places_ai AFTER INSERT ON places BEGIN
                INSERT INTO places_rtree(id, min_lat, max_lat, min_lng, max_lng)
                VALUES (new.id, new.lat, new.lat, new.lng, new.lng);
            END
        ''')

        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS places_au AFTER UPDATE OF lat, lng ON places BEGIN
                UPDATE places_rtree SET min_lat = new.lat, max_lat = new.lat,
                                       min_lng = new.lng, max_lng = new.lng
                WHERE id = new.id;
            END
        ''')

        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS places_ad AFTER DELETE ON places BEGIN
                DELETE FROM places_rtree WHERE id = old.id;
            END
        ''')

        self.conn.commit()
        print("✓ Created places table with R-Tree indexing")

    def import_places(self, places_data: Dict):
        """Import places from JSON into database."""
        cursor = self.conn.cursor()

        # Get places from JSON
        results = places_data.get('results', [])
        categories = places_data.get('categories', {})

        imported = 0
        skipped = 0

        for place in results:
            try:
                name = place.get('name', '')
                if not name:
                    skipped += 1
                    continue

                category = place.get('cat', 'other')
                lat = place.get('lat', 0)
                lng = place.get('lon', 0)

                # Get category details
                cat_info = self.place_categories.get(category, {})
                category_name = cat_info.get('display_name', category)
                icon = cat_info.get('icon', '📍')
                description = cat_info.get('description', '')

                # Prepare tags
                tags = {
                    'original_category': category,
                    'icon': icon,
                    'category_display': category_name
                }

                cursor.execute('''
                    INSERT OR REPLACE INTO places
                    (name, category, category_name, lat, lng, description, icon, tags_json, city)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    name,
                    category,
                    category_name,
                    lat,
                    lng,
                    description,
                    icon,
                    json.dumps(tags, ensure_ascii=False),
                    'بندرعباس'
                ))

                imported += 1

                if imported % 100 == 0:
                    print(f"  ✓ Imported {imported} places...")

            except Exception as e:
                print(f"  ✗ Error importing place {place.get('name', 'unknown')}: {e}")
                skipped += 1

        self.conn.commit()
        print(f"✓ Imported {imported} places (skipped: {skipped})")
        return imported, skipped

    def create_places_view(self):
        """Create view for place statistics and searches."""
        cursor = self.conn.cursor()

        cursor.execute('''
            CREATE VIEW IF NOT EXISTS places_by_category AS
            SELECT
                category,
                category_name,
                COUNT(*) as place_count,
                MIN(lat) as min_lat,
                MAX(lat) as max_lat,
                MIN(lng) as min_lng,
                MAX(lng) as max_lng,
                AVG(lat) as center_lat,
                AVG(lng) as center_lng
            FROM places
            GROUP BY category, category_name
            ORDER BY place_count DESC
        ''')

        cursor.execute('''
            CREATE VIEW IF NOT EXISTS places_search_index AS
            SELECT
                id,
                name,
                category_name,
                category,
                icon,
                lat,
                lng,
                LOWER(name) as search_name
            FROM places
        ''')

        self.conn.commit()
        print("✓ Created places views")

    def get_statistics(self) -> Dict:
        """Get import statistics."""
        cursor = self.conn.cursor()

        # Total places
        cursor.execute("SELECT COUNT(*) as count FROM places")
        total = cursor.fetchone()['count']

        # By category
        cursor.execute('''
            SELECT category_name, COUNT(*) as count
            FROM places
            GROUP BY category_name
            ORDER BY count DESC
        ''')

        by_category = []
        for row in cursor.fetchall():
            by_category.append({
                'category': row['category_name'],
                'count': row['count']
            })

        # Bounding box
        cursor.execute('''
            SELECT
                MIN(lat) as min_lat, MAX(lat) as max_lat,
                MIN(lng) as min_lng, MAX(lng) as max_lng,
                AVG(lat) as center_lat, AVG(lng) as center_lng
            FROM places
        ''')

        bbox = cursor.fetchone()

        return {
            'total': total,
            'by_category': by_category,
            'bbox': dict(bbox) if bbox else None
        }

    def print_statistics(self, stats: Dict):
        """Print formatted statistics."""
        print("\n" + "="*70)
        print("📍 BANDAR ABBAS PLACES IMPORT STATISTICS")
        print("="*70)

        print(f"\n📊 Total Places: {stats['total']}")

        print("\n🗂️  Places by Category:")
        print("-" * 70)
        for item in stats['by_category']:
            icon = next(
                (cat.get('icon', '📍') for cat_key, cat in self.place_categories.items()
                 if cat.get('display_name') == item['category']),
                '📍'
            )
            print(f"  {icon} {item['category']:35} → {item['count']:4} places")

        if stats['bbox']:
            bbox = stats['bbox']
            print(f"\n📐 Geographic Coverage:")
            print(f"  Latitude:  {bbox['min_lat']:.4f} to {bbox['max_lat']:.4f}")
            print(f"  Longitude: {bbox['min_lng']:.4f} to {bbox['max_lng']:.4f}")
            print(f"  Center:    {bbox['center_lat']:.4f}, {bbox['center_lng']:.4f}")

        print("="*70 + "\n")

    def run(self, places_json: str):
        """Execute the import process."""
        try:
            print("🗄️  BANDAR ABBAS PLACES IMPORTER")
            print("="*70)

            # Connect
            print("\n1️⃣  Connecting to database...")
            self.connect()
            print(f"✓ Connected to {self.db_path}")

            # Create table
            print("\n2️⃣  Creating places table...")
            self.create_places_table()

            # Load data
            print("\n3️⃣  Loading places data...")
            places_data = self.load_places(places_json)
            print(f"✓ Loaded {places_data.get('count', 0)} places from JSON")

            # Import
            print("\n4️⃣  Importing places into database...")
            imported, skipped = self.import_places(places_data)

            # Create views
            print("\n5️⃣  Creating database views...")
            self.create_places_view()

            # Statistics
            print("\n6️⃣  Generating statistics...")
            stats = self.get_statistics()
            self.print_statistics(stats)

            print("✅ IMPORT COMPLETED SUCCESSFULLY!")
            print(f"\nNext steps:")
            print(f"  • Query places by category: SELECT * FROM places WHERE category = 'restaurant'")
            print(f"  • Search places: SELECT * FROM places WHERE name LIKE '%کافه%'")
            print(f"  • Find places in area: SELECT * FROM places WHERE lat BETWEEN 27.1 AND 27.2")

            return True

        except Exception as e:
            print(f"\n❌ IMPORT FAILED: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return False
        finally:
            self.close()


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Import 677 Bandar Abbas places into geo.db'
    )
    parser.add_argument(
        '--db',
        default='geo.db',
        help='Path to geo.db database (default: geo.db)'
    )
    parser.add_argument(
        '--places',
        default='bandar_places.json',
        help='Path to places JSON file'
    )

    args = parser.parse_args()

    if not Path(args.places).exists():
        print(f"❌ Places file not found: {args.places}")
        return 1

    importer = BandarAbbasPlacesImporter(args.db)
    success = importer.run(args.places)
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
