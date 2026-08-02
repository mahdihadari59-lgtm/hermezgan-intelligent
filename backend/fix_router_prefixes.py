from pathlib import Path
import re

BASE = Path("app/api/v1")

files = [
    "auth.py",
    "chat.py",
    "locations.py",
    "analytics.py",
    "cameras.py",
    "hotspots.py",
    "endpoints/voice.py",
]

for f in files:
    p = BASE / f
    if not p.exists():
        continue

    text = p.read_text(encoding="utf-8")

    text = re.sub(
        r'APIRouter\s*\(\s*prefix\s*=\s*"[^"]+"\s*,',
        'APIRouter(',
        text,
    )

    text = re.sub(
        r"APIRouter\s*\(\s*prefix\s*=\s*'[^']+'\s*,",
        "APIRouter(",
        text,
    )

    p.write_text(text, encoding="utf-8")
    print(f"✓ {p}")

print("Done.")
