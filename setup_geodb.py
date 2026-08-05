#!/usr/bin/env python3
"""
GEO.DB Complete Setup Script
Automates entire initialization, import, and verification process
"""

import os
import sys
import json
from pathlib import Path
from subprocess import run, CalledProcessError


class GeoDBSetup:
    """Complete setup orchestration."""
    
    def __init__(self):
        self.repo_root = Path(__file__).parent
        self.db_path = self.repo_root / "geo.db"
        self.errors = []
        self.completed_steps = []
    
    def print_banner(self, title: str):
        """Print formatted banner."""
        print("\n" + "="*70)
        print(f"🗄️  {title}")
        print("="*70)
    
    def print_step(self, step_num: int, title: str):
        """Print step header."""
        print(f"\n{step_num}️⃣  {title}")
        print("-" * 70)
    
    def check_dependencies(self) -> bool:
        """Check if all required files exist."""
        self.print_step(1, "Checking Dependencies")
        
        required_files = [
            "database/schema.sql",
            "database/schema_admin_geo.sql",
            "hormozgan_atlas_dictionary.json",
            "bandar_places.json",
            "init_geodb.py",
            "import_hormozgan_atlas.py",
            "import_bandar_places.py",
            "generate_places_kb.py"
        ]
        
        missing = []
        for file in required_files:
            path = self.repo_root / file
            if path.exists():
                print(f"  ✓ {file}")
            else:
                print(f"  ✗ {file} NOT FOUND")
                missing.append(file)
        
        if missing:
            self.errors.append(f"Missing files: {', '.join(missing)}")
            return False
        
        print("\n✅ All dependencies found!")
        self.completed_steps.append("Dependencies check")
        return True
    
    def initialize_database(self) -> bool:
        """Initialize database with schemas."""
        self.print_step(2, "Initializing Database")
        
        try:
            # Remove existing database if force
            if self.db_path.exists():
                print(f"  ⚠️  Database exists, backing up...")
                backup_path = self.db_path.with_suffix(".db.backup")
                self.db_path.rename(backup_path)
                print(f"  ✓ Backup created: {backup_path.name}")
            
            # Run init script
            print(f"\n  Running init_geodb.py...")
            result = run(
                [sys.executable, str(self.repo_root / "init_geodb.py"),
                 "--db", str(self.db_path)],
                capture_output=True,
                text=True,
                cwd=self.repo_root
            )
            
            if result.returncode != 0:
                self.errors.append(f"init_geodb.py failed: {result.stderr}")
                return False
            
            print(result.stdout)
            print("\n✅ Database initialized!")
            self.completed_steps.append("Database initialization")
            return True
            
        except CalledProcessError as e:
            self.errors.append(f"Database initialization failed: {e}")
            return False
        except Exception as e:
            self.errors.append(f"Unexpected error during initialization: {e}")
            return False
    
    def import_atlas_data(self) -> bool:
        """Import Hormozgan atlas data."""
        self.print_step(3, "Importing Hormozgan Atlas Data")
        
        try:
            print(f"  Running import_hormozgan_atlas.py...")
            result = run(
                [sys.executable, str(self.repo_root / "import_hormozgan_atlas.py"),
                 "--db", str(self.db_path),
                 "--atlas", str(self.repo_root / "hormozgan_atlas_dictionary.json")],
                capture_output=True,
                text=True,
                cwd=self.repo_root
            )
            
            if result.returncode != 0:
                self.errors.append(f"import_hormozgan_atlas.py failed: {result.stderr}")
                return False
            
            print(result.stdout)
            print("✅ Atlas data imported!")
            self.completed_steps.append("Hormozgan atlas import")
            return True
            
        except Exception as e:
            self.errors.append(f"Atlas import failed: {e}")
            return False
    
    def import_places_data(self) -> bool:
        """Import Bandar Abbas places."""
        self.print_step(4, "Importing 677 Bandar Abbas Places")
        
        try:
            print(f"  Running import_bandar_places.py...")
            result = run(
                [sys.executable, str(self.repo_root / "import_bandar_places.py"),
                 "--db", str(self.db_path),
                 "--places", str(self.repo_root / "bandar_places.json")],
                capture_output=True,
                text=True,
                cwd=self.repo_root
            )
            
            if result.returncode != 0:
                self.errors.append(f"import_bandar_places.py failed: {result.stderr}")
                return False
            
            print(result.stdout)
            print("✅ Places data imported!")
            self.completed_steps.append("Bandar Abbas places import")
            return True
            
        except Exception as e:
            self.errors.append(f"Places import failed: {e}")
            return False
    
    def generate_knowledge_base(self) -> bool:
        """Generate knowledge base and search index."""
        self.print_step(5, "Generating Knowledge Base & Search Index")
        
        try:
            print(f"  Running generate_places_kb.py...")
            result = run(
                [sys.executable, str(self.repo_root / "generate_places_kb.py"),
                 "--db", str(self.db_path)],
                capture_output=True,
                text=True,
                cwd=self.repo_root
            )
            
            if result.returncode != 0:
                self.errors.append(f"generate_places_kb.py failed: {result.stderr}")
                return False
            
            print(result.stdout)
            print("✅ Knowledge base generated!")
            self.completed_steps.append("Knowledge base generation")
            return True
            
        except Exception as e:
            self.errors.append(f"Knowledge base generation failed: {e}")
            return False
    
    def verify_installation(self) -> bool:
        """Verify complete installation."""
        self.print_step(6, "Verifying Installation")
        
        try:
            import sqlite3
            
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Check tables
            tables_to_check = [
                ('geo_counties', 'Counties'),
                ('geo_islands', 'Islands'),
                ('places', 'Places'),
                ('pois', 'POIs')
            ]
            
            print("\n  📊 Table Statistics:")
            all_good = True
            
            for table, name in tables_to_check:
                try:
                    cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                    count = cursor.fetchone()['count']
                    
                    if count > 0:
                        print(f"    ✓ {name:20} → {count:6} records")
                    else:
                        print(f"    ⚠️  {name:20} → {count:6} records (empty)")
                        all_good = False
                except Exception as e:
                    print(f"    ✗ {name:20} → ERROR: {e}")
                    all_good = False
            
            # Check file sizes
            print("\n  📁 Generated Files:")
            generated_files = [
                ("geo.db", "Database"),
                ("bandar_places_knowledge.json", "Knowledge base"),
                ("bandar_places_search_index.json", "Search index")
            ]
            
            for filename, desc in generated_files:
                path = self.repo_root / filename
                if path.exists():
                    size_mb = path.stat().st_size / (1024 * 1024)
                    print(f"    ✓ {desc:20} → {size_mb:.2f} MB")
                else:
                    print(f"    ✗ {desc:20} → NOT FOUND")
                    all_good = False
            
            conn.close()
            
            if all_good:
                print("\n✅ Installation verified!")
                self.completed_steps.append("Installation verification")
                return True
            else:
                return False
            
        except Exception as e:
            self.errors.append(f"Verification failed: {e}")
            return False
    
    def print_summary(self):
        """Print final summary."""
        self.print_banner("SETUP SUMMARY")
        
        print(f"\n✅ Completed Steps ({len(self.completed_steps)}):")
        for step in self.completed_steps:
            print(f"   ✓ {step}")
        
        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for error in self.errors:
                print(f"   ✗ {error}")
        
        print("\n" + "="*70)
    
    def print_next_steps(self):
        """Print next steps."""
        print("\n📚 Next Steps:")
        print("-" * 70)
        print("  1. Review the documentation:")
        print("     • docs/GEO_DB_GUIDE.md - Comprehensive guide")
        print("     • docs/QUICK_START.md - Quick start examples")
        print()
        print("  2. Use the Python API:")
        print("     • from geodb import Places, Counties, Islands")
        print("     • with Places() as places:")
        print("     •     nearby = places.get_by_location(27.1842, 56.2893)")
        print()
        print("  3. Query the database:")
        print("     • sqlite3 geo.db")
        print("     • SELECT * FROM places WHERE category = 'restaurant';")
        print()
        print("  4. Generate custom reports:")
        print("     • Use Python API for analysis")
        print("     • Export data to JSON/CSV")
        print()
        print("="*70 + "\n")
    
    def run(self) -> bool:
        """Execute complete setup."""
        self.print_banner("GEO.DB COMPLETE SETUP")
        
        steps = [
            ("Checking dependencies", self.check_dependencies),
            ("Initializing database", self.initialize_database),
            ("Importing atlas data", self.import_atlas_data),
            ("Importing places data", self.import_places_data),
            ("Generating knowledge base", self.generate_knowledge_base),
            ("Verifying installation", self.verify_installation)
        ]
        
        success = True
        for description, step_func in steps:
            if not step_func():
                print(f"\n❌ Failed at: {description}")
                success = False
                break
        
        self.print_summary()
        
        if success:
            print("\n🎉 SETUP COMPLETED SUCCESSFULLY!")
            self.print_next_steps()
            return True
        else:
            print("\n⚠️  SETUP INCOMPLETE - Please check errors above")
            return False


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Complete GEO.DB Setup'
    )
    parser.add_argument(
        '--skip-verification',
        action='store_true',
        help='Skip final verification step'
    )
    
    args = parser.parse_args()
    
    setup = GeoDBSetup()
    success = setup.run()
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
