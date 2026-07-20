#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HDP Hybrid Pipeline — Incremental Embedding Builder
Builds embeddings incrementally with checkpoint/resume mechanism.

Author: Mahdi Hadari
Version: 1.1.3
"""

import sqlite3
import logging
import time
import re
import struct
import hashlib
import math
import unicodedata
from typing import Dict, List

from engine.utils import setup_logging, format_duration
from engine.checkpoint import CheckpointManager
from engine.incremental import get_pending_documents
from engine.batch_encoder import BatchEncoder

logger = logging.getLogger(__name__)


class HashingEmbeddingManager:
    """
    Pure-stdlib fallback "embedding" — a feature-hashing bag-of-words vector.
    Not a real semantic embedding model (no PyTorch/sentence-transformers
    available under the Termux/no-pip-deps constraint), but gives a working,
    deterministic, dependency-free default so the pipeline runs end-to-end.
    """
    model_name = "hashing-bow-v1"

    def __init__(self, dim: int = 128):
        self.dim = dim
        self._token_pattern = re.compile(r'\w+', re.UNICODE)
    
    def _normalize_for_hash(self, text: str) -> str:
        """Normalize Persian text for hashing."""
        if not text:
            return ""
        
        # Unicode normalization
        text = unicodedata.normalize('NFC', text)
        
        # Replace Arabic characters with Persian equivalents
        text = text.replace("ي", "ی")
        text = text.replace("ك", "ک")
        text = text.replace("ة", "ه")
        text = text.replace("أ", "ا")
        text = text.replace("إ", "ا")
        text = text.replace("ؤ", "و")
        text = text.replace("ئ", "ی")
        # NOTE: Do NOT replace "آ" with "ا" as it changes meaning (e.g., "آب" -> "اب")
        
        # Remove zero-width characters
        for ch in ['\u200c', '\u200d', '\u200e', '\u200f', '\ufeff']:
            text = text.replace(ch, '')
        
        # Collapse whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def _vector_for(self, text: str) -> List[float]:
        vec = [0.0] * self.dim
        normalized = self._normalize_for_hash(text)
        tokens = self._token_pattern.findall(normalized.lower())
        if not tokens:
            return vec

        for tok in tokens:
            h = int(hashlib.md5(tok.encode('utf-8')).hexdigest(), 16)
            bucket = h % self.dim
            sign = 1.0 if (h // self.dim) % 2 == 0 else -1.0
            vec[bucket] += sign

        # sqrt-scale to dampen high-frequency tokens (poor-man's TF damping)
        return [math.copysign(math.sqrt(abs(v)), v) if v != 0 else 0.0 for v in vec]

    def encode(self, text: str) -> List[float]:
        """Encode a single text to embedding vector."""
        return self._vector_for(text)

    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """Encode a batch of texts to embedding vectors."""
        return [self._vector_for(t) for t in texts]


class IncrementalEmbeddingBuilder:
    """
    Builds embeddings incrementally with checkpoint/resume support.
    
    Features:
    - Resume from last successful run
    - Only processes new/changed documents
    - Batched encoding for efficiency
    - Atomic checkpoint saving
    - Progress tracking and logging
    """
    
    def __init__(
        self,
        db_path: str,
        checkpoint_path: str,
        table_name: str = "knowledge",
        batch_size: int = 64,
        embedding_dim: int = 128,
        embedding_manager = None,
        embedding_type: str = "fallback"
    ):
        """
        Initialize IncrementalEmbeddingBuilder.
        
        Args:
            db_path: Path to SQLite database
            checkpoint_path: Path to checkpoint file
            table_name: Name of the table containing documents
            batch_size: Batch size for encoding
            embedding_dim: Dimension of embeddings
            embedding_manager: Custom embedding manager
            embedding_type: Type of embedding ('fallback', 'incremental', 'gat')
        """
        self.db_path = db_path
        self.table_name = table_name
        self.batch_size = batch_size
        self.embedding_type = embedding_type
        
        # Initialize checkpoint
        self.checkpoint = CheckpointManager(checkpoint_path)
        self.checkpoint.load()
        
        # Initialize embedding manager
        if embedding_manager is None:
            self.embedding_manager = HashingEmbeddingManager(dim=embedding_dim)
        else:
            self.embedding_manager = embedding_manager
        
        # Initialize batch encoder
        self.encoder = BatchEncoder(
            embedding_manager=self.embedding_manager,
            batch_size=batch_size
        )
        
        # Stats
        self.stats = {
            'processed': 0,
            'chunks': 0,
            'errors': 0,
            'start_time': None,
            'end_time': None
        }
        
        logger.info(f"IncrementalEmbeddingBuilder initialized:")
        logger.info(f"  DB: {db_path}")
        logger.info(f"  Table: {table_name}")
        logger.info(f"  Checkpoint: {checkpoint_path}")
        logger.info(f"  Batch size: {batch_size}")
        logger.info(f"  Embedding type: {embedding_type}")
        logger.info(f"  Model: {self.embedding_manager.model_name}")
    
    def build(self, force: bool = False) -> Dict:
        """
        Build embeddings incrementally.
        
        Args:
            force: If True, rebuild all embeddings regardless of checkpoint
            
        Returns:
            Dict with statistics
        """
        self.stats['start_time'] = time.time()
        
        logger.info(f"Starting {'full rebuild' if force else 'incremental'} embedding build...")
        
        conn = None
        try:
            # Connect to database
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            
            # Get pending documents
            pending = get_pending_documents(
                conn=conn,
                table=self.table_name,
                checkpoint=self.checkpoint,
                force=force
            )
            
            if not pending:
                logger.info("No pending documents to process")
                self.stats['end_time'] = time.time()
                return self.get_stats()
            
            logger.info(f"Found {len(pending)} pending documents to process")
            
            # Process documents in batches
            total_docs = len(pending)
            processed = 0
            
            # Create index on node_id if not exists (for performance)
            self._ensure_index(conn)
            
            for i in range(0, total_docs, self.batch_size):
                batch = pending[i:i + self.batch_size]
                batch_size = len(batch)
                
                # Extract texts for embedding (title + content for better quality)
                texts = [f"{doc['title']}\n{doc['content']}" for doc in batch]
                
                try:
                    # Generate embeddings
                    embeddings = self.encoder.encode_all(texts)
                    
                    # Save embeddings
                    for doc, embedding in zip(batch, embeddings):
                        self._save_embedding(
                            conn=conn,
                            doc_id=doc['id'],
                            content_hash=doc['content_hash'],
                            embedding=embedding
                        )
                        
                        processed += 1
                        self.stats['processed'] += 1
                        self.stats['chunks'] += 1
                    
                    # Commit after each batch
                    conn.commit()
                    
                    # Update checkpoint after each batch
                    for doc in batch:
                        self.checkpoint.mark_done(
                            doc_id=doc['id'],
                            content_hash=doc['content_hash'],
                            n_chunks=1
                        )
                    self.checkpoint.save()
                    
                    # Log progress
                    elapsed = time.time() - self.stats['start_time']
                    logger.info(
                        f"Progress: {processed}/{total_docs} documents "
                        f"({processed/total_docs*100:.1f}%) - "
                        f"Elapsed: {format_duration(elapsed)}"
                    )
                    
                except Exception as e:
                    logger.error(f"Error processing batch starting at {i}: {e}")
                    self.stats['errors'] += batch_size
                    conn.rollback()
                    continue
            
            logger.info(f"✅ Embedding build completed: {processed} documents processed")
            
        except Exception as e:
            logger.error(f"Fatal error during build: {e}")
            if conn:
                conn.rollback()
            raise
        
        finally:
            self.stats['end_time'] = time.time()
            if conn:
                conn.close()
        
        return self.get_stats()
    
    def _ensure_index(self, conn: sqlite3.Connection):
        """Ensure index on node_id for performance."""
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_embeddings_node_id 
                ON knowledge_embeddings(node_id)
            """)
            conn.commit()
        except Exception as e:
            logger.warning(f"Could not create index: {e}")
    
    def _save_embedding(
        self,
        conn: sqlite3.Connection,
        doc_id: int,
        content_hash: str,
        embedding: List[float]
    ):
        """
        Save embedding to database using INSERT OR REPLACE.
        
        Args:
            conn: Database connection
            doc_id: Document ID
            content_hash: Content hash (used as checksum)
            embedding: Embedding vector
        """
        cursor = conn.cursor()
        
        # Convert embedding to blob
        embedding_blob = struct.pack(f'{len(embedding)}f', *embedding)
        
        # Use content_hash as checksum
        checksum = content_hash
        
        # Use INSERT OR REPLACE for better performance
        cursor.execute("""
            INSERT OR REPLACE INTO knowledge_embeddings (
                node_id,
                embedding,
                dimension,
                embedding_type,
                checksum,
                updated_at
            ) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            str(doc_id),
            embedding_blob,
            len(embedding),
            self.embedding_type,
            checksum
        ))
    
    def get_stats(self) -> Dict:
        """Get build statistics."""
        elapsed = 0
        if self.stats['start_time'] and self.stats['end_time']:
            elapsed = self.stats['end_time'] - self.stats['start_time']
        elif self.stats['start_time']:
            elapsed = time.time() - self.stats['start_time']
        
        return {
            'processed': self.stats['processed'],
            'chunks': self.stats['chunks'],
            'errors': self.stats['errors'],
            'duration_seconds': elapsed,
            'duration_formatted': format_duration(elapsed),
            'checkpoint': self.checkpoint.summary(),
            'model': self.embedding_manager.model_name,
            'embedding_type': self.embedding_type
        }
    
    def reset_checkpoint(self):
        """Reset checkpoint to start fresh."""
        self.checkpoint.reset()
        self.checkpoint.save()
        logger.info("Checkpoint reset successfully")


def main():
    """Main entry point for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='HDP Incremental Embedding Builder'
    )
    parser.add_argument(
        '--db',
        default='data/hdp_v2.db',
        help='Path to SQLite database'
    )
    parser.add_argument(
        '--checkpoint',
        default='data/embedding_checkpoint.json',
        help='Path to checkpoint file'
    )
    parser.add_argument(
        '--table',
        default='knowledge',
        help='Name of the table containing documents'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=64,
        help='Batch size for encoding'
    )
    parser.add_argument(
        '--dim',
        type=int,
        default=128,
        help='Embedding dimension'
    )
    parser.add_argument(
        '--embedding-type',
        default='fallback',
        choices=['fallback', 'incremental', 'gat'],
        help='Type of embedding to store (default: fallback)'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force rebuild all embeddings'
    )
    parser.add_argument(
        '--reset',
        action='store_true',
        help='Reset checkpoint and exit'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(level)
    
    # Create builder
    builder = IncrementalEmbeddingBuilder(
        db_path=args.db,
        checkpoint_path=args.checkpoint,
        table_name=args.table,
        batch_size=args.batch_size,
        embedding_dim=args.dim,
        embedding_type=args.embedding_type
    )
    
    # Handle reset
    if args.reset:
        builder.reset_checkpoint()
        return
    
    # Build embeddings
    stats = builder.build(force=args.force)
    
    # Print final stats
    print("\n" + "=" * 60)
    print("📊 BUILD STATISTICS")
    print("=" * 60)
    print(f"✅ Processed: {stats['processed']:,} documents")
    print(f"📦 Chunks: {stats['chunks']:,}")
    print(f"❌ Errors: {stats['errors']:,}")
    print(f"⏱️  Duration: {stats['duration_formatted']}")
    print(f"📁 Checkpoint: {stats['checkpoint']['completed_documents']} completed")
    print(f"🏷️  Embedding Type: {stats['embedding_type']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
