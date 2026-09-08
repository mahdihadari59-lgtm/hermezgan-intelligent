from __future__ import annotations

from pathlib import Path


def test_database_path_is_resolved(db_path: Path):
    assert db_path == db_path.resolve()
