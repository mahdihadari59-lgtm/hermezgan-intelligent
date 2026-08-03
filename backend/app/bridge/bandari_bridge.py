
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Bandari Engine Bridge
Connects Bandari dialect engine to HDP backend
"""

import sys
from pathlib import Path

BANDARI_PATH = Path.home() / "hermezgan-intelligent" / "bandari-engine-2026" / "bandari-engine"

if BANDARI_PATH.exists():
    sys.path.insert(0, str(BANDARI_PATH))

try:
    from bandari_core import BandariEngine
    BANDARI_ENGINE = BandariEngine()
except ImportError:
    BANDARI_ENGINE = None
    print("Bandari engine not available")

def translate_to_bandari(text):
    if BANDARI_ENGINE:
        return BANDARI_ENGINE.translate(text)
    return text

def translate_to_persian(text):
    if BANDARI_ENGINE:
        return BANDARI_ENGINE.to_persian(text)
    return text
