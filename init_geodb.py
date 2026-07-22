#!/usr/bin/env python3
"""
Initialize geo.db with both spatial and administrative schemas
Applies base schema and admin geography schema, then imports Hormozgan atlas data
"""

import sqlite3
import json
import sys
from pathlib import Path
from typing import Optional

class GeoDBInitializer:
    def __init__(self, db_path: str = "geo.db"):
        self.db_path = db_path
        self.conn = None

    def connect(self):
        """Connect to the database."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self.conn

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()

    def execute_sql_file(self, sql_file: str, description: str = ""):
        """Execute SQL commands from a file."""
        if not Path(sql_file).exists():
            print(f"✗ SQL file not found: {sql_file}")
            return False
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        try:
            cursor = self.conn.cursor()
            # Split by semicolon and execute each statement
            statements = [s.strip() for s in sql_content.split(';') if s.strip()]
            for statement in statements:
                cursor.execute(statement)
            self.conn.commit()
            desc = f" - {description}" if description else ""
            print(f"✓ Applied {sql_file}{desc}")
            return True
        except Exception as e:
            print(f"✗ Error applying {sql_file}: {e}")
            return False

    def verify_tables(self):
        """Verify all required tables exist."""
        cursor = self.conn.cursor()
        
        required_tables = [
            'pois', 'traffic', 'cameras', 'hospitals', 'fuel_stations', 'roads',
            'geo_counties', 'geo_islands'
        ]
        
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name NOT LIKE '%_rtree'
        """)
        
        existing_tables = {row['name'] for row in cursor.fetchall()}
        
        print("\n" + "="*60)
        print("TABLE VERIFICATION")
        print("="*60)
        
        missing = []
        for table in required_tables:
            if table in existing_tables:
                cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                count = cursor.fetchone()['count']
                print(f"✓ {table:25} ({count:6} rows)")
            else:
                missing.append(table)
                print(f"✗ {table:25} (MISSING)")
        
        print("="*60)
        return len(missing) == 0

    def get_statistics(self):
        """Get database statistics."""
        cursor = self.conn.cursor()
        
        stats = {}
        
        # County statistics
        cursor.execute("SELECT COUNT(*) as count FROM geo_counties")
        stats['counties'] = cursor.fetchone()['count']
        
        # Island statistics
        cursor.execute("SELECT COUNT(*) as count FROM geo_islands")
        stats['islands'] = cursor.fetchone()['count']
        
        # Island distribution by county
        cursor.execute("""
            SELECT gc.name, COUNT(gi.id) as island_count
            FROM geo_counties gc
            LEFT JOIN geo_islands gi ON gc.id = gi.county_id
            GROUP BY gc.id, gc.name
            ORDER BY island_count DESC
        """)
        
        stats['islands_by_county'] = []
        for row in cursor.fetchall():
            stats['islands_by_county'].append({
                'county': row['name'],
                'count': row['island_count']
            })
        
        # POI statistics
        cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM pois
            GROUP BY category
            ORDER BY count DESC
        """)
        
        stats['pois_by_category'] = {}
        for row in cursor.fetchall():
            stats['pois_by_category'][row['category']] = row['count']
        
        return stats

    def print_statistics(self, stats: dict):
        """Print formatted statistics."""
        print("\n" + "="*60)
        print("GEOGRAPHIC DATA SUMMARY")
        print("="*60)
        
        print(f"\n📍 Counties: {stats['counties']}")
        print(f"🏝️  Islands: {stats['islands']}")
        
        print("\n📊 Islands by County:")
        for item in stats['islands_by_county']:
            if item['count'] > 0:
                print(f"   • {item['county']:20} → {item['count']:2} islands")
            else:
                print(f"   • {item['county']:20} → no islands")
        
        print("\n🗂️  POIs by Category:")
        total_pois = 0
        for category, count in sorted(stats['pois_by_category'].items(), key=lambda x: x[1], reverse=True):
            print(f"   • {category:35} → {count:6} items")
            total_pois += count
        print(f"   {'TOTAL':35} → {total_pois:6} items")
        
        print("="*60)

    def run(self, base_schema: str = "database/schema.sql", 
            admin_schema: str = "database/schema_admin_geo.sql"):
        """Execute the full initialization process."""
        try:
            print("🗄️  GEO.DB INITIALIZATION")
            print("="*60)
            
            # Connect to database
            print("\n1️⃣  Connecting to database...")
            self.connect()
            
            # Enable WAL mode
            cursor = self.conn.cursor()
            cursor.execute("PRAGMA journal_mode = WAL")
            cursor.execute("PRAGMA foreign_keys = ON")
            self.conn.commit()
            print("✓ Database connected with WAL mode enabled")
            
            # Apply base schema
            print("\n2️⃣  Applying base spatial schema...")
            if not self.execute_sql_file(base_schema, "Spatial R-Tree indexing"):
                raise Exception("Failed to apply base schema")
            
            # Apply admin geo schema
            print("\n3️⃣  Applying administrative geography schema...")
            if not self.execute_sql_file(admin_schema, "Counties and Islands"):
                raise Exception("Failed to apply admin schema")
            
            # Verify tables
            print("\n4️⃣  Verifying database structure...")
            if not self.verify_tables():
                raise Exception("Some required tables are missing")
            
            # Get statistics
            print("\n5️⃣  Generating statistics...")
            stats = self.get_statistics()
            self.print_statistics(stats)
            
            print("\n✅ INITIALIZATION COMPLETED SUCCESSFULLY!")
            print(f"\n📦 Database ready at: {self.db_path}")
            print("\nNext steps:")
            print("  • Use import_hormozgan_atlas.py to import atlas data")
            print("  • Query geo_counties and geo_islands tables")
            print("  • Use spatial queries with R-Tree indexes for performance")
            
            return True
            
        except Exception as e:
            print(f"\n❌ INITIALIZATION FAILED: {e}", file=sys.stderr)
            return False
        finally:
            self.close()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Initialize geo.db with spatial and administrative schemas'
    )
    parser.add_argument(
        '--db',
        default='geo.db',
        help='Path to geo.db database (default: geo.db)'
    )
    parser.add_argument(
        '--base-schema',
        default='database/schema.sql',
        help='Path to base schema SQL file'
    )
    parser.add_argument(
        '--admin-schema',
        default='database/schema_admin_geo.sql',
        help='Path to admin geography schema SQL file'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Overwrite existing database'
    )
    
    args = parser.parse_args()
    
    # Check if database exists and warn
    if Path(args.db).exists() and not args.force:
        print(f"⚠️  Database already exists: {args.db}")
        response = input("Overwrite? (y/N): ").lower()
        if response != 'y':
            print("Cancelled.")
            return 1
        Path(args.db).unlink()
    
    initializer = GeoDBInitializer(args.db)
    success = initializer.run(args.base_schema, args.admin_schema)
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
