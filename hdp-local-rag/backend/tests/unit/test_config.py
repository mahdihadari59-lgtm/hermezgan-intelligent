from __future__ import annotations

from pathlib import Path


def test_db_path_points_to_file(db_path: Path):
    assert db_path.exists()
    assert db_path.is_file()
