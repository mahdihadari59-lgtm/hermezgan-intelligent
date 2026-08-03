#!/usr/bin/env python3

from pathlib import Path

ROOT = Path.home() / "hermezgan-intelligent"

CHECKS = [
    ROOT / "backend",
    ROOT / "backend/data/hdp_v2.db",
    ROOT / "bandari-engine-2026",
    ROOT / "backend/app/main.py",
    ROOT / "backend/app/core/orchestrator_v2.py",
]

ok = True
for item in CHECKS:
    if item.exists():
        print("[ OK ]", item)
    else:
        print("[FAIL]", item)
        ok = False

exit(0 if ok else 1)
