#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HDP Hybrid Pipeline — Shared Utilities
Pure stdlib only (no external pip dependencies), per Termux constraints.

Author: Mahdi Hadari
Version: 1.0.0
"""

import hashlib
import json
import logging
import math
import os
import re
import tempfile
import unicodedata
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Persian zero-width characters that cause false "content changed" positives
# if not stripped before hashing (ZWNJ, ZWJ, and a couple of look-alike marks
# that show up from copy-pasted Persian text on Android keyboards).
_ZERO_WIDTH_CHARS = ['\u200c', '\u200d', '\u200e', '\u200f', '\ufeff']


def setup_logging(level=logging.INFO):
    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%H:%M:%S'
    )


def normalize_for_hash(text: str) -> str:
    """Normalize Persian text before hashing so invisible-character noise
    (ZWNJ/ZWJ variants) doesn't trigger spurious re-indexing in incremental.py."""
    if not text:
        return ""
    text = unicodedata.normalize('NFC', text)
    for ch in _ZERO_WIDTH_CHARS:
        text = text.replace(ch, '')
    # collapse repeated whitespace so pure formatting edits don't count as changes
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def sha256_content(text: str) -> str:
    """Stable content hash used by incremental.py to detect changed documents."""
    normalized = normalize_for_hash(text)
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()


def atomic_write_json(path: str, data: Dict):
    """Write JSON via a temp file + os.replace so a crash mid-write (e.g. a
    killed Termux session) never leaves a half-written, corrupt checkpoint."""
    directory = os.path.dirname(path) or '.'
    os.makedirs(directory, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=directory, prefix='.tmp_', suffix='.json')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, path)  # atomic on POSIX (Termux/Android included)
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise


def read_json(path: str) -> Optional[Dict]:
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def format_duration(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes, sec = divmod(int(seconds), 60)
    if minutes < 60:
        return f"{minutes}m {sec}s"
    hours, minutes = divmod(minutes, 60)
    return f"{hours}h {minutes}m"


class HashingEmbeddingManager:
    """
    Pure-stdlib fallback "embedding" — a feature-hashing bag-of-words vector.
    Not a real semantic embedding model (no PyTorch/sentence-transformers
    available under the Termux/no-pip-deps constraint), but gives a working,
    deterministic, dependency-free default so the pipeline runs end-to-end.

    Replace `embedding_manager=` in build_embeddings.py with your real model
    (e.g. an API-backed one) once/if a network-based option becomes viable.
    """
    model_name = "hashing-bow-v1"

    def __init__(self, dim: int = 128):
        self.dim = dim
        self._token_pattern = re.compile(r'\w+', re.UNICODE)

    def _vector_for(self, text: str) -> List[float]:
        vec = [0.0] * self.dim
        tokens = self._token_pattern.findall(normalize_for_hash(text).lower())
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
        return self._vector_for(text)

    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        return [self._vector_for(t) for t in texts]
