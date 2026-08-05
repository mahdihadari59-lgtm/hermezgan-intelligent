#!/usr/bin/env python3
"""
Import Hormozgan Atlas data into geo.db
Populates counties, islands, and POIs from hormozgan_atlas_dictionary.json
"""

import json
import sqlite3
import sys
from pathlib import Path
from typing import Optional

class HormozganAtlasImporter:
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

    def load_atlas(self, json_path: str) -> dict:
        """Load Hormozgan atlas JSON file."""
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def import_counties(self, atlas: dict):
        """Import counties into pois table."""
        cursor = self.conn.cursor()
        counties = atlas.get('counties', [])
        
        for county in counties:
            try:
                # Store counties as POIs with category 'administrative/county'
                cursor.execute('''
                    INSERT OR REPLACE INTO pois 
                    (category, name, lat, lng, description, tags_json, tenant_uuid)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    'administrative/county',
                    county['name'],
                    county['lat'],
                    county['lon'],
                    f"County: {county['name']} (Center: {county['center']})",
                    json.dumps({
                        'id': county['id'],
                        'aliases': county.get('aliases', []),
                        'type': county['type'],
                        'center': county['center'],
                        'en_name': county.get('name')
                    }),
                    'hormozgan'
                ))
                print(f"✓ Imported county: {county['name']}")
            except Exception as e:
                print(f"✗ Error importing county {county['name']}: {e}")
        
        self.conn.commit()

    def import_islands(self, atlas: dict):
        """Import islands into pois table."""
        cursor = self.conn.cursor()
        islands = atlas.get('islands', [])
        
        for island in islands:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO pois 
                    (category, name, lat, lng, description, tags_json, tenant_uuid)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    'administrative/island',
                    island['name'],
                    island['lat'],
                    island['lon'],
                    f"Island: {island['name']} (County: {island['county']})",
                    json.dumps({
                        'id': island['id'],
                        'county': island['county'],
                        'aliases': island.get('aliases', []),
                        'type': island['type']
                    }),
                    'hormozgan'
                ))
                print(f"✓ Imported island: {island['name']}")
            except Exception as e:
                print(f"✗ Error importing island {island['name']}: {e}")
        
        self.conn.commit()

    def create_geo_admin_tables(self):
        """Create additional administrative geography tables."""
        cursor = self.conn.cursor()
        
        # Create counties table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS geo_counties (
                id              INTEGER PRIMARY KEY,
                name            TEXT NOT NULL UNIQUE,
                name_en         TEXT,
                province        TEXT NOT NULL DEFAULT 'هرمزگان',
                center          TEXT,
                lat             REAL NOT NULL,
                lng             REAL NOT NULL,
                aliases_json    TEXT,
                area_km2        REAL,
                population      INTEGER,
                updated_at      INTEGER NOT NULL DEFAULT (strftime('%s','now'))
            )
        ''')
        
        # Create islands table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS geo_islands (
                id              INTEGER PRIMARY KEY,
                name            TEXT NOT NULL UNIQUE,
                county_id       INTEGER NOT NULL REFERENCES geo_counties(id) ON DELETE CASCADE,
                lat             REAL NOT NULL,
                lng             REAL NOT NULL,
                aliases_json    TEXT,
                area_km2        REAL,
                population      INTEGER,
                type            TEXT DEFAULT 'island',
                updated_at      INTEGER NOT NULL DEFAULT (strftime('%s','now'))
            )
        ''')
        
        # Create indexes for geo_counties
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_geo_counties_name ON geo_counties(name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_geo_counties_latlng ON geo_counties(lat, lng)')
        
        # Create indexes for geo_islands
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_geo_islands_name ON geo_islands(name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_geo_islands_county ON geo_islands(county_id)')
        
        self.conn.commit()
        print("✓ Created geo_counties and geo_islands tables")

    def populate_geo_admin_tables(self, atlas: dict):
        """Populate administrative geography tables."""
        cursor = self.conn.cursor()
        
        # Import counties
        counties = atlas.get('counties', [])
        for county in counties:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO geo_counties 
                    (id, name, center, lat, lng, aliases_json)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    county['id'],
                    county['name'],
                    county['center'],
                    county['lat'],
                    county['lon'],
                    json.dumps(county.get('aliases', []))
                ))
            except Exception as e:
                print(f"✗ Error importing county {county['name']}: {e}")
        
        # Import islands with county references
        islands = atlas.get('islands', [])
        for island in islands:
            try:
                # Find county_id by name
                county_name = island['county']
                cursor.execute('SELECT id FROM geo_counties WHERE name = ?', (county_name,))
                county_row = cursor.fetchone()
                county_id = county_row['id'] if county_row else None
                
                if county_id is None:
                    print(f"⚠ Warning: County '{county_name}' not found for island '{island['name']}'")
                    continue
                
                cursor.execute('''
                    INSERT OR REPLACE INTO geo_islands 
                    (id, name, county_id, lat, lng, aliases_json, type)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    island['id'],
                    island['name'],
                    county_id,
                    island['lat'],
                    island['lon'],
                    json.dumps(island.get('aliases', [])),
                    island.get('type', 'island')
                ))
            except Exception as e:
                print(f"✗ Error importing island {island['name']}: {e}")
        
        self.conn.commit()
        print(f"✓ Populated geo_counties with {len(counties)} entries")
        print(f"✓ Populated geo_islands with {len(islands)} entries")

    def verify_import(self):
        """Verify imported data."""
        cursor = self.conn.cursor()
        
        cursor.execute('SELECT COUNT(*) as count FROM geo_counties')
        county_count = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM geo_islands')
        island_count = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM pois WHERE category LIKE "administrative%"')
        admin_pois = cursor.fetchone()['count']
        
        print("\n" + "="*50)
        print("IMPORT VERIFICATION")
        print("="*50)
        print(f"Counties imported: {county_count}")
        print(f"Islands imported: {island_count}")
        print(f"Administrative POIs: {admin_pois}")
        print("="*50)

    def run(self, atlas_json: str):
        """Execute the import process."""
        try:
            print("Connecting to database...")
            self.connect()
            
            print("Loading Hormozgan atlas data...")
            atlas = self.load_atlas(atlas_json)
            
            print("Creating administrative geography tables...")
            self.create_geo_admin_tables()
            
            print("Importing counties...")
            self.import_counties(atlas)
            
            print("Importing islands...")
            self.import_islands(atlas)
            
            print("Populating administrative tables...")
            self.populate_geo_admin_tables(atlas)
            
            print("Verifying import...")
            self.verify_import()
            
            print("\n✓ Import completed successfully!")
            return True
            
        except Exception as e:
            print(f"\n✗ Import failed: {e}", file=sys.stderr)
            return False
        finally:
            self.close()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Import Hormozgan atlas data into geo.db'
    )
    parser.add_argument(
        '--db',
        default='geo.db',
        help='Path to geo.db database (default: geo.db)'
    )
    parser.add_argument(
        '--atlas',
        default='hormozgan_atlas_dictionary.json',
        help='Path to Hormozgan atlas JSON file'
    )
    
    args = parser.parse_args()
    
    importer = HormozganAtlasImporter(args.db)
    success = importer.run(args.atlas)
    sys.exit(0 if success else 1)
