#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HDP Hybrid Pipeline — Incremental Indexing
Compares each document's current content hash against the hash recorded in
the checkpoint; only new or changed documents are returned for re-embedding.

Author: Mahdi Hadari
Version: 1.0.0
"""

import logging
import sqlite3
from typing import Dict, List

from engine.utils import sha256_content
from engine.checkpoint import CheckpointManager

logger = logging.getLogger(__name__)


def get_pending_documents(conn: sqlite3.Connection, table: str,
                          checkpoint: CheckpointManager,
                          force: bool = False) -> List[Dict]:
    """
    Returns a list of dicts: {id, title, content, category, content_hash}
    for every document that is new or whose content changed since the
    last checkpoint. If force=True, every document is returned regardless
    of checkpoint state (full rebuild).
    """
    cursor = conn.cursor()

    # Try with is_deleted column first (soft delete support)
    try:
        cursor.execute(f"""
            SELECT
                id,
                title,
                content,
                category
            FROM {table}
            WHERE
                is_deleted = 0
                AND content IS NOT NULL
                AND TRIM(content) != ''
        """)
    except sqlite3.OperationalError:
        # Fallback: table doesn't have is_deleted column
        cursor.execute(f"""
            SELECT
                id,
                title,
                content,
                category
            FROM {table}
            WHERE
                content IS NOT NULL
                AND TRIM(content) != ''
        """)

    rows = cursor.fetchall()

    pending = []
    skipped = 0

    for doc_id, title, content, category in rows:
        content_hash = sha256_content(content)

        if not force:
            existing_hash = checkpoint.get_hash(doc_id)
            if existing_hash == content_hash:
                skipped += 1
                continue

        pending.append({
            'id': doc_id,
            'title': title,
            'content': content,
            'category': category,
            'content_hash': content_hash
        })

    logger.info(f"Incremental scan: {len(rows)} total, {len(pending)} pending "
                f"(new/changed), {skipped} unchanged (skipped)"
                f"{' [FORCE: skip disabled]' if force else ''}")

    return pending


if __name__ == "__main__":
    import tempfile, os
    logging.basicConfig(level=logging.INFO)

    tmp_db = os.path.join(tempfile.mkdtemp(), "test.db")
    conn = sqlite3.connect(tmp_db)
    conn.execute("CREATE TABLE knowledge (id INTEGER PRIMARY KEY, title TEXT, content TEXT, category TEXT)")
    conn.execute("INSERT INTO knowledge VALUES (1, 't1', 'محتوای اول', 'cat')")
    conn.execute("INSERT INTO knowledge VALUES (2, 't2', 'محتوای دوم', 'cat')")
    conn.commit()

    cp_path = os.path.join(tempfile.mkdtemp(), "cp.json")
    cp = CheckpointManager(cp_path)
    cp.load()

    # first run: everything is pending
    pending1 = get_pending_documents(conn, "knowledge", cp)
    assert len(pending1) == 2
    for doc in pending1:
        cp.mark_done(doc['id'], doc['content_hash'], 1)
    cp.save()

    # second run, nothing changed: nothing pending
    pending2 = get_pending_documents(conn, "knowledge", cp)
    assert len(pending2) == 0

    # change doc 1's content -> should reappear as pending
    conn.execute("UPDATE knowledge SET content = 'محتوای تغییر یافته' WHERE id = 1")
    conn.commit()

    pending3 = get_pending_documents(conn, "knowledge", cp)
    assert len(pending3) == 1 and pending3[0]['id'] == 1

    print("✅ incremental change-detection works as expected")
