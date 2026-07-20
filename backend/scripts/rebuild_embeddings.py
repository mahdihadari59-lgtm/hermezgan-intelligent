#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
===========================================================
HDP v2 Embedding Rebuilder
Version : 2.3 Production (Local Embedding - Termux Compatible)
Author  : HDP AI Core

هدف:

بازسازی امن جدول knowledge_embeddings

بدون تغییر هیچ جدول دیگری

کاملاً سازگار با:

SQLite
Termux
Python 3.13+
بدون وابستگی PyTorch/SentenceTransformer/FastEmbed
HDP v2 Database

===========================================================

این اسکریپت فقط روی جدول‌های زیر کار می‌کند:

knowledge
knowledge_embeddings

هیچ تغییری روی:

knowledge_fts
knowledge_graph
knowledge_search
knowledge_links
knowledge_nodes
knowledge_edges
graph_*
traffic_*
entity_*

انجام نخواهد داد.

===========================================================
"""

from __future__ import annotations

import os
import sys
import json
import time
import sqlite3
import hashlib
import logging
import traceback
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field

import numpy as np

try:
    from tqdm import tqdm
except ImportError:
    print("Installing tqdm...")
    os.system(f"{sys.executable} -m pip install tqdm")
    from tqdm import tqdm


# =============================================================
# Local Embedding (Pure Python, No External Dependencies)
# =============================================================

class LocalEmbedding:
    """
    Embedding سبک برای Termux
    از SHA256 برای تولید بردارهای تعیین‌کننده (Deterministic) استفاده می‌کند
    بدون نیاز به PyTorch، SentenceTransformer یا FastEmbed
    """

    def __init__(self, dim: int = 384):
        self.dim = dim
        self.model_name = "local-hashing-v1"

    def embed(self, text: str) -> np.ndarray:
        """
        تولید بردار embedding از متن با استفاده از SHA256
        خروجی: numpy array با ابعاد self.dim نرمال‌شده
        """
        if not text:
            return np.zeros(self.dim, dtype=np.float32)

        # هش SHA256 متن
        h = hashlib.sha256(text.encode("utf-8")).digest()

        # استفاده از هش به عنوان seed برای تولید اعداد تصادفی
        seed = int.from_bytes(h[:8], "little")

        rng = np.random.default_rng(seed)

        # تولید بردار نرمال
        vec = rng.normal(size=self.dim).astype(np.float32)

        # نرمال‌سازی
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec /= norm

        return vec

    def embed_batch(self, texts: List[str]) -> List[np.ndarray]:
        """تولید embedding برای چند متن به صورت دسته‌ای"""
        return [self.embed(text) for text in texts]


# =============================================================
# Configuration
# =============================================================

@dataclass
class Config:
    """Production configuration for embedding rebuilder"""
    
    # Database
    DATABASE: str = "hdp_v2.db"
    
    # Embedding
    EMBEDDING_DIM: int = 384
    
    # Processing
    BATCH_SIZE: int = 256
    COMMIT_INTERVAL: int = 10
    RESUME: bool = True
    SAVE_STATE_INTERVAL: int = 100
    
    # Embedding
    STORE_BINARY: bool = True
    HASH: str = "sha256"
    
    # Files
    STATE_FILE: str = "backend/.embedding_state.json"
    LOG_FILE: str = "backend/rebuild_embeddings.log"
    
    # SQLite
    SQLITE_TIMEOUT: int = 120
    CACHE_SIZE: int = -64000
    SYNCHRONOUS: str = "NORMAL"
    JOURNAL: str = "WAL"
    TEMP_STORE: int = 2
    MMAP_SIZE: int = 30000000000
    
    # Behaviour
    SKIP_EMPTY: bool = True
    SKIP_SHORT: bool = True
    MIN_CONTENT_LENGTH: int = 10
    VERIFY_AFTER_WRITE: bool = False
    ENABLE_PROGRESS: bool = True
    ENABLE_HASH_CHECK: bool = True
    ENABLE_LOG: bool = True
    ENABLE_RESUME: bool = True
    
    @classmethod
    def from_args(cls, args) -> 'Config':
        """Create config from command line arguments"""
        config = cls()
        if args.db:
            config.DATABASE = args.db
        if args.batch:
            config.BATCH_SIZE = args.batch
        if args.dim:
            config.EMBEDDING_DIM = args.dim
        if args.no_resume:
            config.ENABLE_RESUME = False
        return config


CONFIG = Config()


# =============================================================
# Logger Setup
# =============================================================

def setup_logger():
    """Setup logger with file and console handlers"""
    logger = logging.getLogger("HDP")
    logger.setLevel(logging.INFO)
    
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )
    
    # File handler
    log_dir = Path(CONFIG.LOG_FILE).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    file_handler = logging.FileHandler(
        CONFIG.LOG_FILE,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


LOGGER = setup_logger()


# =============================================================
# Resume Manager
# =============================================================

class ResumeManager:
    """Manage resume state for interrupted runs"""
    
    def __init__(self):
        self.file = Path(CONFIG.STATE_FILE)
    
    def load(self) -> Dict[str, Any]:
        """Load resume state"""
        if not CONFIG.ENABLE_RESUME:
            return {"last_id": 0, "processed": 0, "updated": 0}
        
        if not self.file.exists():
            return {"last_id": 0, "processed": 0, "updated": 0}
        
        try:
            with open(self.file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"last_id": 0, "processed": 0, "updated": 0}
    
    def save(self, last_id: int, processed: int, updated: int) -> None:
        """Save resume state"""
        data = {
            "last_id": last_id,
            "processed": processed,
            "updated": updated,
            "time": datetime.now().isoformat()
        }
        self.file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    
    def clear(self) -> None:
        """Clear resume state"""
        if self.file.exists():
            self.file.unlink()


# =============================================================
# Database Manager
# =============================================================

class DatabaseManager:
    """SQLite database connection manager"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or CONFIG.DATABASE
        self.conn = None
        self.cursor = None
    
    def connect(self) -> sqlite3.Connection:
        """Establish database connection"""
        self.conn = sqlite3.connect(
            self.db_path,
            timeout=CONFIG.SQLITE_TIMEOUT
        )
        self.conn.row_factory = sqlite3.Row
        
        # Optimize SQLite settings
        self.conn.execute(f"PRAGMA journal_mode={CONFIG.JOURNAL}")
        self.conn.execute(f"PRAGMA synchronous={CONFIG.SYNCHRONOUS}")
        self.conn.execute(f"PRAGMA cache_size={CONFIG.CACHE_SIZE}")
        self.conn.execute(f"PRAGMA temp_store={CONFIG.TEMP_STORE}")
        self.conn.execute(f"PRAGMA mmap_size={CONFIG.MMAP_SIZE}")
        self.conn.execute("PRAGMA foreign_keys=ON")
        
        self.cursor = self.conn.cursor()
        return self.conn
    
    def close(self) -> None:
        """Close database connection"""
        if self.conn:
            self.conn.commit()
            self.conn.close()
    
    def execute(self, sql: str, params: tuple = ()):
        """Execute SQL and return cursor"""
        return self.conn.execute(sql, params)
    
    def commit(self) -> None:
        """Commit transaction"""
        self.conn.commit()


# =============================================================
# Schema Manager
# =============================================================

class SchemaManager:
    """Manage database schema verification"""
    
    REQUIRED_COLUMNS = ["id", "title", "content"]
    
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.cursor = db.cursor
    
    def table_exists(self, table_name: str) -> bool:
        """Check if table exists"""
        self.cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,)
        )
        return self.cursor.fetchone() is not None
    
    def column_names(self, table_name: str) -> List[str]:
        """Get column names for a table"""
        self.cursor.execute(f"PRAGMA table_info({table_name})")
        return [row["name"] for row in self.cursor]
    
    def verify_knowledge(self) -> None:
        """Verify knowledge table schema"""
        if not self.table_exists("knowledge"):
            raise RuntimeError("Table 'knowledge' not found.")
        
        cols = self.column_names("knowledge")
        missing = [col for col in self.REQUIRED_COLUMNS if col not in cols]
        
        if missing:
            raise RuntimeError(f"Knowledge schema invalid: {', '.join(missing)}")
        
        LOGGER.info("✅ knowledge table verified")
    
    def create_embedding_table(self) -> None:
        """Create embedding table if not exists"""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_embeddings(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                knowledge_id INTEGER UNIQUE NOT NULL,
                embedding BLOB NOT NULL,
                text_hash TEXT NOT NULL,
                model_version TEXT,
                dimension INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(knowledge_id)
                REFERENCES knowledge(id)
                ON DELETE CASCADE
            )
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_embedding_kid
            ON knowledge_embeddings(knowledge_id)
        """)
        
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_embedding_hash
            ON knowledge_embeddings(text_hash)
        """)
        
        self.db.commit()
        LOGGER.info("✅ knowledge_embeddings table ready")
    
    def verify_embedding_table(self) -> None:
        """Verify embedding table schema"""
        if not self.table_exists("knowledge_embeddings"):
            LOGGER.info("knowledge_embeddings missing, creating...")
            self.create_embedding_table()
            return
        
        cols = self.column_names("knowledge_embeddings")
        required = ["knowledge_id", "embedding", "text_hash"]
        missing = [c for c in required if c not in cols]
        
        if missing:
            raise RuntimeError(f"knowledge_embeddings invalid: {', '.join(missing)}")
        
        LOGGER.info("✅ knowledge_embeddings verified")
    
    def total_knowledge(self) -> int:
        """Get total knowledge records"""
        self.cursor.execute("SELECT COUNT(*) FROM knowledge")
        return self.cursor.fetchone()[0]
    
    def total_embeddings(self) -> int:
        """Get total embeddings"""
        self.cursor.execute("SELECT COUNT(*) FROM knowledge_embeddings")
        return self.cursor.fetchone()[0]
    
    def report(self) -> None:
        """Print database report"""
        LOGGER.info("")
        LOGGER.info("📊 Database Report")
        LOGGER.info("-" * 40)
        LOGGER.info(f"  Knowledge   : {self.total_knowledge():,}")
        LOGGER.info(f"  Embeddings  : {self.total_embeddings():,}")
        LOGGER.info("")
    
    def initialize(self) -> None:
        """Initialize all schemas"""
        self.verify_knowledge()
        self.verify_embedding_table()
        self.report()


# =============================================================
# Hash Engine
# =============================================================

class HashEngine:
    """Content hash generation"""
    
    @staticmethod
    def sha256(text: str) -> str:
        """Generate SHA256 hash of text"""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()
    
    @staticmethod
    def md5(text: str) -> str:
        """Generate MD5 hash of text"""
        return hashlib.md5(text.encode("utf-8")).hexdigest()
    
    @classmethod
    def hash_text(cls, text: str, method: str = "sha256") -> str:
        """Hash text with specified method"""
        if method == "md5":
            return cls.md5(text)
        return cls.sha256(text)


# =============================================================
# Text Builder
# =============================================================

class TextBuilder:
    """Build text from knowledge record"""
    
    @staticmethod
    def clean(value: Any) -> str:
        """Clean and normalize text"""
        if value is None:
            return ""
        value = str(value)
        value = value.replace("\r", " ")
        value = value.replace("\n", " ")
        value = value.replace("\t", " ")
        return value.strip()
    
    @classmethod
    def build(cls, row: Dict[str, Any]) -> str:
        """Build combined text from record"""
        parts = []
        
        # Title
        title = cls.clean(row.get("title", ""))
        if title:
            parts.append(title)
        
        # Content
        content = cls.clean(row.get("content", ""))
        if content:
            parts.append(content)
        
        # Category
        category = cls.clean(row.get("category", ""))
        if category:
            parts.append(category)
        
        # Subcategory
        subcategory = cls.clean(row.get("subcategory", ""))
        if subcategory:
            parts.append(subcategory)
        
        # City
        city = cls.clean(row.get("city", ""))
        if city:
            parts.append(city)
        
        # Keywords
        keywords = cls.clean(row.get("keywords", ""))
        if keywords:
            parts.append(keywords)
        
        # Topic
        topic = cls.clean(row.get("topic", ""))
        if topic:
            parts.append(topic)
        
        # Tags
        tags = cls.clean(row.get("tags", ""))
        if tags:
            parts.append(tags)
        
        return "\n".join(parts).strip()


# =============================================================
# Validator
# =============================================================

class Validator:
    """Validate records before processing"""
    
    @classmethod
    def validate(cls, row: Dict[str, Any]) -> bool:
        """Check if record should be processed"""
        if row.get("id") is None:
            return False
        
        title = row.get("title", "") or ""
        content = row.get("content", "") or ""
        
        if CONFIG.SKIP_EMPTY:
            if len(title.strip()) == 0 and len(content.strip()) == 0:
                return False
        
        if CONFIG.SKIP_SHORT:
            if len(content.strip()) < CONFIG.MIN_CONTENT_LENGTH:
                return False
        
        return True


# =============================================================
# Batch Reader
# =============================================================

class BatchReader:
    """Read records in batches"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def read(self, last_id: int, batch_size: int = None) -> List[Dict[str, Any]]:
        """Read next batch of records"""
        batch_size = batch_size or CONFIG.BATCH_SIZE
        
        cursor = self.db.execute("""
            SELECT
                id,
                title,
                content,
                category,
                subcategory,
                city,
                keywords,
                topic,
                tags
            FROM knowledge
            WHERE id > ?
            ORDER BY id
            LIMIT ?
        """, (last_id, batch_size))
        
        return [dict(row) for row in cursor]


# =============================================================
# Embedding Lookup
# =============================================================

class EmbeddingLookup:
    """Check existing embeddings"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
    
    def get_hash(self, knowledge_id: int) -> Optional[str]:
        """Get existing text hash for record"""
        cursor = self.db.execute("""
            SELECT text_hash
            FROM knowledge_embeddings
            WHERE knowledge_id = ?
            LIMIT 1
        """, (knowledge_id,))
        
        row = cursor.fetchone()
        return row["text_hash"] if row else None
    
    def exists(self, knowledge_id: int) -> bool:
        """Check if embedding exists"""
        return self.get_hash(knowledge_id) is not None


# =============================================================
# Local Embedding Model Wrapper
# =============================================================

class EmbeddingModel:
    """Wrapper for LocalEmbedding model"""
    
    def __init__(self, dim: int = 384):
        self.dim = dim
        self.model_name = "local-hashing-v1"
        self.model = LocalEmbedding(dim=dim)
    
    def embed(self, text: str) -> np.ndarray:
        """Generate embedding for a single text"""
        return self.model.embed(text)
    
    def embed_batch(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings for multiple texts"""
        return self.model.embed_batch(texts)


# =============================================================
# Main Embedding Engine
# =============================================================

class EmbeddingEngine:
    """Main embedding engine with LocalEmbedding support"""
    
    def __init__(self, config: Config = None):
        self.config = config or CONFIG
        self.db = DatabaseManager(self.config.DATABASE)
        self.model = None
        self.resume = ResumeManager()
        self.schema = None
        
        # Statistics
        self.processed = 0
        self.skipped = 0
        self.errors = 0
        self.unchanged = 0
        self.last_id = 0
        
        LOGGER.info("🚀 Embedding Engine initialized")
    
    def load_model(self) -> None:
        """Load LocalEmbedding model"""
        if self.model:
            return
        
        self.model = EmbeddingModel(dim=self.config.EMBEDDING_DIM)
        LOGGER.info(f"✅ LocalEmbedding loaded (dim={self.config.EMBEDDING_DIM})")
    
    def initialize(self) -> None:
        """Initialize database and schema"""
        self.db.connect()
        self.schema = SchemaManager(self.db)
        self.schema.initialize()
        
        # Load resume state
        state = self.resume.load()
        self.last_id = state.get("last_id", 0)
        LOGGER.info(f"📌 Resuming from ID: {self.last_id}")
    
    def build_text(self, row: Dict[str, Any]) -> str:
        """Build text from record"""
        return TextBuilder.build(row)
    
    def hash_text(self, text: str) -> str:
        """Generate hash of text"""
        return HashEngine.hash_text(text, method=self.config.HASH)
    
    def get_existing_hash(self, knowledge_id: int) -> Optional[str]:
        """Get existing hash from database"""
        cursor = self.db.execute("""
            SELECT text_hash
            FROM knowledge_embeddings
            WHERE knowledge_id = ?
        """, (knowledge_id,))
        
        row = cursor.fetchone()
        return row["text_hash"] if row else None
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding vector using LocalEmbedding"""
        return self.model.embed(text)
    
    def generate_batch_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings for batch"""
        return self.model.embed_batch(texts)
    
    def save_embedding(self, knowledge_id: int, vector: np.ndarray, text_hash: str) -> None:
        """Save embedding to database"""
        blob = vector.astype(np.float32).tobytes()
        dimension = len(vector)
        
        self.db.execute("""
            INSERT INTO knowledge_embeddings(
                knowledge_id,
                embedding,
                text_hash,
                model_version,
                dimension,
                created_at,
                updated_at
            )
            VALUES(?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ON CONFLICT(knowledge_id)
            DO UPDATE SET
                embedding = excluded.embedding,
                text_hash = excluded.text_hash,
                model_version = excluded.model_version,
                dimension = excluded.dimension,
                updated_at = CURRENT_TIMESTAMP
        """, (
            knowledge_id,
            sqlite3.Binary(blob),
            text_hash,
            self.model.model_name,
            dimension
        ))
    
    def process_batch_fast(self, batch: List[Dict[str, Any]]) -> bool:
        """Process a batch of records using batch mode"""
        if not batch:
            return True
        
        try:
            # Prepare texts and records
            valid_records = []
            texts = []
            
            for row in batch:
                if not Validator.validate(row):
                    self.skipped += 1
                    continue
                
                text = self.build_text(row)
                if not text:
                    self.skipped += 1
                    continue
                
                # Check hash
                new_hash = self.hash_text(text)
                existing_hash = self.get_existing_hash(row["id"])
                
                if CONFIG.ENABLE_HASH_CHECK and existing_hash == new_hash:
                    self.unchanged += 1
                    continue
                
                valid_records.append({
                    "row": row,
                    "text": text,
                    "hash": new_hash
                })
                texts.append(text)
            
            if not valid_records:
                return True
            
            # Batch generate embeddings
            self.db.execute("BEGIN")
            
            try:
                embeddings = self.generate_batch_embeddings(texts)
                
                for i, record in enumerate(valid_records):
                    self.save_embedding(
                        record["row"]["id"],
                        embeddings[i],
                        record["hash"]
                    )
                    self.processed += 1
                    self.last_id = record["row"]["id"]
                
                self.db.commit()
                
                # Save state
                if self.processed % CONFIG.SAVE_STATE_INTERVAL == 0:
                    self.resume.save(self.last_id, self.processed, self.processed)
                
                return True
                
            except Exception as e:
                self.db.execute("ROLLBACK")
                LOGGER.error(f"Batch failed: {e}")
                return False
                
        except Exception as e:
            LOGGER.error(f"Batch processing error: {e}")
            return False
    
    def rebuild(self) -> bool:
        """Main rebuild process"""
        try:
            self.initialize()
            self.load_model()
            
            total = self.schema.total_knowledge()
            LOGGER.info(f"📊 Total knowledge records: {total:,}")
            
            # Create progress bar
            progress = tqdm(
                total=total,
                initial=self.last_id,
                desc="Embedding",
                unit="records",
                disable=not CONFIG.ENABLE_PROGRESS
            )
            
            # Process in batches
            batch_reader = BatchReader(self.db)
            
            while True:
                batch = batch_reader.read(self.last_id)
                
                if not batch:
                    break
                
                ok = self.process_batch_fast(batch)
                self.last_id = batch[-1]["id"]
                
                if not ok:
                    LOGGER.error("❌ Batch processing failed")
                    break
                
                progress.update(len(batch))
                progress.set_postfix({
                    "processed": self.processed,
                    "errors": self.errors,
                    "skipped": self.skipped
                })
            
            progress.close()
            
            # Final report
            self.print_report()
            
            # Clear resume on success
            if self.errors == 0:
                self.resume.clear()
                LOGGER.info("✅ Resume state cleared")
            
            return True
            
        except Exception as e:
            LOGGER.error(f"❌ Rebuild failed: {e}")
            LOGGER.error(traceback.format_exc())
            return False
        
        finally:
            self.db.close()
    
    def print_report(self) -> None:
        """Print final report"""
        LOGGER.info("")
        LOGGER.info("=" * 60)
        LOGGER.info("📊 Embedding Build Report")
        LOGGER.info("=" * 60)
        LOGGER.info(f"  ✅ Processed  : {self.processed:,}")
        LOGGER.info(f"  ⏭️  Skipped    : {self.skipped:,}")
        LOGGER.info(f"  🔄 Unchanged  : {self.unchanged:,}")
        LOGGER.info(f"  ❌ Errors     : {self.errors:,}")
        LOGGER.info(f"  📍 Last ID    : {self.last_id:,}")
        LOGGER.info("=" * 60)


# =============================================================
# Main Entry Point
# =============================================================

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="HDP v2 Embedding Rebuilder (LocalEmbedding - Termux Compatible)"
    )
    
    parser.add_argument(
        "--db",
        default="hdp_v2.db",
        help="SQLite database path"
    )
    
    parser.add_argument(
        "--batch",
        type=int,
        default=32,
        help="Batch size for processing"
    )
    
    parser.add_argument(
        "--dim",
        type=int,
        default=384,
        help="Embedding dimension (default: 384)"
    )
    
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset resume state"
    )
    
    parser.add_argument(
        "--no-resume",
        action="store_true",
        help="Disable resume"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    return parser.parse_args()


def main():
    """Main entry point"""
    args = parse_args()
    
    # Update config
    CONFIG.DATABASE = args.db
    CONFIG.BATCH_SIZE = args.batch
    CONFIG.EMBEDDING_DIM = args.dim
    CONFIG.ENABLE_RESUME = not args.no_resume
    
    if args.verbose:
        LOGGER.setLevel(logging.DEBUG)
    
    # Reset resume state
    if args.reset:
        ResumeManager().clear()
        LOGGER.info("✅ Resume state cleared")
        return
    
    # Print banner
    print()
    print("=" * 60)
    print("🚀 HDP v2 Embedding Rebuilder")
    print("=" * 60)
    print(f"  📁 Database : {CONFIG.DATABASE}")
    print(f"  📊 Batch    : {CONFIG.BATCH_SIZE}")
    print(f"  📐 Dim      : {CONFIG.EMBEDDING_DIM}")
    print(f"  🔄 Resume   : {CONFIG.ENABLE_RESUME}")
    print("=" * 60)
    print()
    
    # Run rebuild
    start_time = time.time()
    engine = EmbeddingEngine(CONFIG)
    success = engine.rebuild()
    elapsed = time.time() - start_time
    
    # Final summary
    print()
    print("=" * 60)
    print("✅ Build Complete" if success else "❌ Build Failed")
    print("=" * 60)
    print(f"  ⏱️  Elapsed  : {elapsed:.2f} seconds")
    print("=" * 60)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
