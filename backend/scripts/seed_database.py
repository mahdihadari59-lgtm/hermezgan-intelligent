"""Database Seeding Script - Populate with initial data"""

import sqlite3
import json
from pathlib import Path
from loguru import logger

DATABASE_PATH = Path(__file__).parent.parent / "hermezgan.db"
SCHEMA_PATH = Path(__file__).parent.parent.parent / "database" / "schema.sql"
SEEDS_PATH = Path(__file__).parent.parent.parent / "database" / "seeds"

def init_database():
    """Initialize database with schema"""
    logger.info(f"🗄️ Initializing database at {DATABASE_PATH}...")
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Read and execute schema
        with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
            schema = f.read()
        
        cursor.executescript(schema)
        conn.commit()
        
        logger.info("✅ Database schema created successfully")
        return conn
    
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
        return None

def seed_entities(conn):
    """Seed entities from JSON files"""
    logger.info("🌱 Seeding entities...")
    
    try:
        entities_file = SEEDS_PATH / "organizations.json"
        
        if not entities_file.exists():
            logger.warning(f"Entities file not found: {entities_file}")
            return
        
        with open(entities_file, 'r', encoding='utf-8') as f:
            entities = json.load(f)
        
        cursor = conn.cursor()
        
        for entity in entities:
            cursor.execute("""
                INSERT OR IGNORE INTO entities 
                (name, name_en, type, category, description, address, phone, latitude, longitude)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entity.get('name'),
                entity.get('name_en'),
                entity.get('type'),
                entity.get('category'),
                entity.get('description'),
                entity.get('address'),
                entity.get('phone'),
                entity.get('latitude'),
                entity.get('longitude'),
            ))
        
        conn.commit()
        logger.info(f"✅ Seeded {len(entities)} entities")
    
    except Exception as e:
        logger.error(f"Seeding error: {e}")

def main():
    """Main seeding function"""
    logger.info("🚀 Starting database seeding...")
    
    conn = init_database()
    if not conn:
        logger.error("❌ Failed to initialize database")
        return
    
    seed_entities(conn)
    
    conn.close()
    logger.info("✅ Database seeding complete!")

if __name__ == "__main__":
    main()
