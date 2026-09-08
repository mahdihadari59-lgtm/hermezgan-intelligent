#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HDP Hybrid Pipeline — Checkpoint / Resume
Tracks which doc_ids have already been embedded (and their content hash),
so a killed/interrupted Termux run can resume without redoing finished work
and without re-embedding unchanged documents.

Author: Mahdi Hadari
Version: 1.0.0
"""

import logging
import threading
import time
from typing import Dict, Optional

from engine.utils import atomic_write_json, read_json

logger = logging.getLogger(__name__)


class CheckpointManager:

    def __init__(self, path: str):
        self.path = path
        self.lock = threading.RLock()
        self.state: Dict = {
            'completed_doc_ids': [],
            'doc_hashes': {},      # doc_id(str) -> content_hash
            'chunks_per_doc': {},  # doc_id(str) -> chunk count (for stats)
            'last_updated': None,
            'started_at': None,
        }

    def load(self) -> bool:
        """Load existing checkpoint if present. Returns True if a resumable
        checkpoint was found, False if starting fresh."""
        data = read_json(self.path)
        if data:
            self.state.update(data)
            logger.info(f"Checkpoint loaded: {len(self.state['completed_doc_ids'])} "
                        f"documents already done")
            return True
        self.state['started_at'] = time.time()
        return False

    def save(self):
        with self.lock:
            self.state['last_updated'] = time.time()
            atomic_write_json(self.path, self.state)

    def is_done(self, doc_id) -> bool:
        """
        Returns True if the document has already been successfully indexed.
        Handles both int and str document IDs consistently.
        """
        with self.lock:
            doc_id = str(doc_id)
            completed = {str(x) for x in self.state["completed_doc_ids"]}

            return (
                doc_id in self.state["doc_hashes"]
                and doc_id in completed
            )

    def get_hash(self, doc_id) -> Optional[str]:
        with self.lock:
            return self.state['doc_hashes'].get(str(doc_id))

    def mark_done(self, doc_id, content_hash: str, n_chunks: int):
        with self.lock:
            doc_id = str(doc_id)
            if doc_id not in self.state['completed_doc_ids']:
                self.state['completed_doc_ids'].append(doc_id)
            self.state['doc_hashes'][doc_id] = content_hash
            self.state['chunks_per_doc'][doc_id] = n_chunks

    def reset(self):
        with self.lock:
            self.state = {
                'completed_doc_ids': [],
                'doc_hashes': {},
                'chunks_per_doc': {},
                'last_updated': None,
                'started_at': time.time()
            }

    def summary(self) -> Dict:
        with self.lock:
            return {
                'completed_documents': len(self.state['completed_doc_ids']),
                'total_chunks': sum(self.state['chunks_per_doc'].values()),
                'started_at': self.state.get('started_at'),
                'last_updated': self.state.get('last_updated'),
            }


if __name__ == "__main__":
    import tempfile, os
    logging.basicConfig(level=logging.INFO)

    tmp = os.path.join(tempfile.mkdtemp(), "checkpoint.json")
    cp = CheckpointManager(tmp)
    cp.load()
    cp.mark_done(1, "hash1", 3)
    cp.mark_done(2, "hash2", 5)
    cp.save()

    cp2 = CheckpointManager(tmp)
    resumed = cp2.load()
    print(f"resumed={resumed}, summary={cp2.summary()}")
    assert cp2.get_hash(1) == "hash1"
    print("✅ checkpoint save/load roundtrip OK")
