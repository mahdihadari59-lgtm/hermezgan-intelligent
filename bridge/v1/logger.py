#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
bridge/v1/logger.py

HDP Bridge Logger
"""

import logging
from pathlib import Path

# ==========================================================
# PATH
# ==========================================================

LOG_DIR = Path(__file__).resolve().parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "bridge.log"

# ==========================================================
# LOGGER
# ==========================================================

LOGGER = logging.getLogger("HDPBridge")

LOGGER.setLevel(logging.INFO)

if not LOGGER.handlers:

    formatter = logging.Formatter(

        "[%(asctime)s] %(levelname)s :: %(message)s",

        "%Y-%m-%d %H:%M:%S",

    )

    file_handler = logging.FileHandler(
        LOG_FILE,
        encoding="utf-8",
    )

    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()

    console_handler.setFormatter(formatter)

    LOGGER.addHandler(file_handler)
    LOGGER.addHandler(console_handler)

# ==========================================================
# HELPERS
# ==========================================================

def info(msg):
    LOGGER.info(msg)


def warning(msg):
    LOGGER.warning(msg)


def error(msg):
    LOGGER.error(msg)


def debug(msg):
    LOGGER.debug(msg)


def exception(msg):
    LOGGER.exception(msg)


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    info("Bridge Logger Started")

    warning("Example Warning")

    error("Example Error")

    debug("Example Debug")
