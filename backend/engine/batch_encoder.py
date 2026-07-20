#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HDP Hybrid Pipeline — Batch Encoder
Wraps an embedding_manager's encode_batch/encode with configurable batch
size and simple retry-with-backoff (useful if embedding_manager ever talks
to a flaky local model server instead of pure in-process code).

Author: Mahdi Hadari
Version: 1.0.3
"""

import logging
import time
import math
from typing import Iterator, List, Any, Dict, Optional
from collections.abc import Sequence as SequenceABC

logger = logging.getLogger(__name__)


class BatchEncoder:
    """
    Batch encoder with validation, retry, and error handling.
    Validates embedding output to ensure data integrity.
    """

    def __init__(
        self,
        embedding_manager,
        batch_size: int = 64,
        max_retries: int = 2,
        retry_backoff: float = 0.5,
        validate: bool = True,
        expected_dim: Optional[int] = None
    ):
        """
        Initialize BatchEncoder.
        
        Args:
            embedding_manager: Manager with encode() and optionally encode_batch()
            batch_size: Number of texts per batch (must be > 0)
            max_retries: Maximum retry attempts on failure (must be >= 0)
            retry_backoff: Backoff multiplier between retries
            validate: Whether to validate embedding output
            expected_dim: Expected embedding dimension (auto-detected if None)
            
        Raises:
            ValueError: If batch_size <= 0 or max_retries < 0
        """
        # Validate parameters
        if batch_size <= 0:
            raise ValueError(f"batch_size must be greater than zero, got {batch_size}")
        if max_retries < 0:
            raise ValueError(f"max_retries must be >= 0, got {max_retries}")
        
        self.embedding_manager = embedding_manager
        self.batch_size = batch_size
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff
        self.validate = validate
        
        # Detect if batch encoding is available
        self._has_batch = hasattr(embedding_manager, 'encode_batch')
        
        # Auto-detect expected dimension from embedding manager
        self._expected_dim = expected_dim
        if self._expected_dim is None:
            self._expected_dim = getattr(embedding_manager, 'dim', None)
            if self._expected_dim is not None:
                logger.info(f"Auto-detected embedding dimension: {self._expected_dim}")
        
        logger.info(
            f"BatchEncoder initialized: batch_size={batch_size}, "
            f"batch_encoding={self._has_batch}, validate={validate}, "
            f"expected_dim={self._expected_dim}"
        )

    def _batched(self, seq: List, size: int) -> Iterator[List]:
        """Yield batches of given size from sequence."""
        for i in range(0, len(seq), size):
            yield seq[i:i + size]

    def _validate_embeddings(self, embeddings: Any, expected_count: int) -> List[List[float]]:
        """
        Validate embedding output for consistency.
        
        Args:
            embeddings: List of embedding vectors
            expected_count: Expected number of embeddings
            
        Returns:
            Validated embeddings as list of lists
            
        Raises:
            RuntimeError: If validation fails
            TypeError: If type is incorrect
            ValueError: If values are invalid
        """
        # Check None
        if embeddings is None:
            raise RuntimeError("Embedding manager returned None")
        
        # Check count
        if len(embeddings) != expected_count:
            raise RuntimeError(
                f"Embedding count mismatch: expected {expected_count}, got {len(embeddings)}"
            )
        
        # Convert to list if needed
        if not isinstance(embeddings, list):
            embeddings = list(embeddings)
        
        # Check each embedding
        for i, emb in enumerate(embeddings):
            # Check if it's a sequence
            if not isinstance(emb, SequenceABC):
                raise TypeError(
                    f"Embedding at index {i} must be a sequence, got {type(emb)}"
                )
            
            # Convert to list if needed
            if not isinstance(emb, list):
                emb = list(emb)
                embeddings[i] = emb
            
            # Check empty
            if not emb:
                raise ValueError(f"Embedding at index {i} is empty")
            
            # Check all elements are numeric and finite
            for j, val in enumerate(emb):
                if not isinstance(val, (int, float)):
                    raise TypeError(
                        f"Embedding[{i}][{j}] must be numeric, got {type(val)}"
                    )
                if not math.isfinite(val):
                    raise ValueError(
                        f"Embedding[{i}][{j}] contains NaN or Infinity: {val}"
                    )
        
        # Check consistent dimension
        if embeddings:
            first_dim = len(embeddings[0])
            if self._expected_dim is None:
                self._expected_dim = first_dim
                logger.info(f"Detected embedding dimension: {self._expected_dim}")
            elif first_dim != self._expected_dim:
                raise RuntimeError(
                    f"Inconsistent embedding dimension: expected {self._expected_dim}, "
                    f"got {first_dim} at index 0"
                )
            
            # Check all have same dimension
            for i, emb in enumerate(embeddings):
                if len(emb) != self._expected_dim:
                    raise RuntimeError(
                        f"Inconsistent dimension at index {i}: "
                        f"expected {self._expected_dim}, got {len(emb)}"
                    )
        
        return embeddings

    def encode_all(self, texts: List[str]) -> List[List[float]]:
        """
        Encode a list of texts, batching to respect batch_size.
        
        Args:
            texts: List of text strings to encode
            
        Returns:
            List of embedding vectors
            
        Raises:
            TypeError: If texts is not a list of strings
            RuntimeError: If encoding fails after retries
        """
        if not texts:
            return []
        
        # Validate input types
        if not isinstance(texts, list):
            raise TypeError(f"texts must be a list, got {type(texts)}")
        
        if not all(isinstance(t, str) for t in texts):
            raise TypeError("All elements in texts must be strings")

        results: List[List[float]] = []

        for batch in self._batched(texts, self.batch_size):
            embeddings = self._encode_batch_with_retry(batch)
            
            # Validate if enabled
            if self.validate:
                embeddings = self._validate_embeddings(embeddings, len(batch))
            
            results.extend(embeddings)

        return results

    def _encode_batch_with_retry(self, batch: List[str]) -> List[List[float]]:
        """
        Encode a batch with retry logic.
        
        Args:
            batch: List of texts to encode
            
        Returns:
            List of embedding vectors
            
        Raises:
            RuntimeError: If all retry attempts fail
        """
        attempt = 0
        
        while True:
            try:
                if self._has_batch:
                    return self.embedding_manager.encode_batch(batch)
                else:
                    return [self.embedding_manager.encode(t) for t in batch]
                    
            except Exception as e:
                attempt += 1
                
                if attempt > self.max_retries:
                    logger.error(
                        f"Batch encode failed after {attempt} attempts: {e}"
                    )
                    raise RuntimeError(f"Encoding failed after {attempt} attempts") from e
                
                wait = self.retry_backoff * attempt
                logger.warning(
                    f"Batch encode error (attempt {attempt}/{self.max_retries}): "
                    f"{e} — retrying in {wait:.1f}s"
                )
                time.sleep(wait)

    def set_expected_dim(self, dim: int):
        """
        Set expected embedding dimension for validation.
        
        Args:
            dim: Expected dimension
        """
        self._expected_dim = dim
        logger.info(f"Expected embedding dimension set to {dim}")

    def get_stats(self) -> Dict:
        """Get encoder statistics."""
        return {
            'batch_size': self.batch_size,
            'max_retries': self.max_retries,
            'has_batch_encoding': self._has_batch,
            'validate': self.validate,
            'expected_dim': self._expected_dim,
            'model': getattr(self.embedding_manager, 'model_name', 'unknown')
        }


if __name__ == "__main__":
    # Test with fallback embedding manager
    logging.basicConfig(level=logging.INFO)
    
    from engine.utils import HashingEmbeddingManager
    
    # Create embedding manager
    embedder = HashingEmbeddingManager(dim=128)
    
    # Create encoder
    encoder = BatchEncoder(
        embedding_manager=embedder,
        batch_size=4,
        max_retries=2,
        retry_backoff=0.1,
        validate=True
    )
    
    # Test encoding
    texts = ["هرمزگان", "بندرعباس", "قشم", "کیش", "جزیره هرمز"]
    embeddings = encoder.encode_all(texts)
    
    print(f"\n✅ Encoded {len(embeddings)} texts")
    print(f"   Dimension: {len(embeddings[0]) if embeddings else 0}")
    print(f"   Stats: {encoder.get_stats()}")
    
    # Test validation failure
    print("\n🧪 Testing validation...")
    try:
        class BadEmbedder:
            model_name = "bad"
            def encode_batch(self, texts):
                return [[0.1] * 128 for _ in texts] + [[0.2] * 128]  # extra embedding
        
        bad_encoder = BatchEncoder(BadEmbedder(), batch_size=2, validate=True)
        bad_encoder.encode_all(["a", "b"])
    except Exception as e:
        print(f"✅ Caught validation error: {e}")
