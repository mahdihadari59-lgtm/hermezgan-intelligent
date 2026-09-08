#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
cd "$(dirname "$0")"

# This script assumes the release ZIP was extracted directly into backend/.
# It preserves the existing FastAPI app and only adds the Bandari router once.

ROUTERS="app/api/v1/routers.py"
if [ ! -f "$ROUTERS" ]; then
  echo "ERROR: $ROUTERS not found. Run from backend/" >&2
  exit 1
fi

python - "$ROUTERS" <<'PY'
from pathlib import Path
import sys
p=Path(sys.argv[1])
s=p.read_text(encoding='utf-8')
imp='from app.api.v1.endpoints.bandari import router as bandari_router'
if imp not in s:
    s += '\n' + imp + '\n'
if 'router.include_router(bandari_router)' not in s:
    s += '\nrouter.include_router(bandari_router)\n'
p.write_text(s,encoding='utf-8')
PY

# Remove Node client module from this Bandari service directory only if it exists.
# Other project files are not deleted.
rm -f app/services/bandari/bandari_client.py

python -m compileall -q \
  app/services/bandari \
  app/api/v1/endpoints/bandari.py \
  app/api/v1/bandari_v2.py \
  app/schemas/bandari.py

echo "Bandari v6 Python internal migration installed."
echo "Run: python scripts/init_bandari_v6_db.py"
echo "Then start: python -m uvicorn app.main:app --host 0.0.0.0 --port 8001"
