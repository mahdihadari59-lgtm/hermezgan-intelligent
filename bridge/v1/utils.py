#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
bridge/v1/utils.py

Utility functions for HDP Bridge
"""

from pathlib import Path
import sqlite3
import hashlib
import json
from typing import Any, Dict, List


# ==========================================================
# PATH
# ==========================================================

def ensure_path(path):

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(path)

    return path


# ==========================================================
# SQLITE
# ==========================================================

def sqlite_version():

    return sqlite3.sqlite_version


def row_to_dict(row):

    if row is None:
        return None

    return dict(row)


def rows_to_dict(rows):

    return [dict(r) for r in rows]


# ==========================================================
# JSON
# ==========================================================

def save_json(path, data):

    path = Path(path)

    path.write_text(

        json.dumps(

            data,

            ensure_ascii=False,

            indent=2,

        ),

        encoding="utf-8",

    )


def load_json(path):

    return json.loads(

        Path(path).read_text(

            encoding="utf-8"

        )

    )


# ==========================================================
# HASH
# ==========================================================

def sha256(text):

    return hashlib.sha256(

        text.encode("utf-8")

    ).hexdigest()


# ==========================================================
# DATABASE INFO
# ==========================================================

def database_size(path):

    path = Path(path)

    if not path.exists():
        return 0

    return path.stat().st_size


def human_size(size):

    units = [

        "B",

        "KB",

        "MB",

        "GB",

        "TB",

    ]

    size = float(size)

    for unit in units:

        if size < 1024:
            return f"{size:.2f} {unit}"

        size /= 1024

    return f"{size:.2f} PB"


# ==========================================================
# TABLE HELPERS
# ==========================================================

def format_table_list(tables):

    return "\n".join(

        f"• {t}"

        for t in tables

    )


# ==========================================================
# DEBUG
# ==========================================================

def print_header(title):

    print()

    print("=" * 60)

    print(title)

    print("=" * 60)

    print()


def print_key_values(data: Dict[str, Any]):

    for k, v in data.items():

        print(f"{k:<20} : {v}")


# ==========================================================
# VALIDATION
# ==========================================================

def is_sqlite(path):

    path = Path(path)

    if not path.exists():
        return False

    try:

        with path.open("rb") as f:

            header = f.read(16)

        return header.startswith(b"SQLite format")

    except Exception:

        return False


# ==========================================================
# VERSION
# ==========================================================

__version__ = "1.0.0"


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    print_header("HDP Utils")

    print("SQLite Version :", sqlite_version())
