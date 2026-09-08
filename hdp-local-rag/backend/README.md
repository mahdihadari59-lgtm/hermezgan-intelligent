# HDP Bandari v6 Python Internal Migration

Extract this ZIP directly into the existing `backend/` directory.

```bash
cd ~/hermezgan-intelligent/backend
unzip -o /path/to/hdp-bandari-v6-python-internal.zip
bash install_bandari_v6_internal.sh
python scripts/init_bandari_v6_db.py
python -m compileall -q app/services/bandari app/api/v1/endpoints/bandari.py app/api/v1/bandari_v2.py app/schemas/bandari.py
```

The existing FastAPI entrypoint remains `app.main:app` on port `8001`.

Bandari is now internal Python/FastAPI and does not use Node.js or `:5200`.

Endpoints:

- GET `/api/v1/bandari/v2/health`
- POST `/api/v1/bandari/v2/translate`
- POST `/api/v1/bandari/v2/detect`
- GET `/api/v1/bandari/v2/search`
- GET `/api/v1/bandari/v2/categories`
- GET `/api/v1/bandari/v2/knowledge`
- GET `/api/v1/bandari/v2/stats`

The installer only modifies the existing `app/api/v1/routers.py` to register the Bandari router once. It does not alter `app/server.py`.
