name=docs/INSTALL.md
# Install and run (Release v1.0.0)

Prereqs:
- Docker & docker-compose
- Python 3.11 (for local dev)
- Node 18 (for frontend/bandari engine builds)

Local development with docker-compose:

  docker compose -f infra/docker-compose.dev.yml up --build

Backend local (without docker):

  cd backend
  python -m venv .venv
  source .venv/bin/activate
  pip install -r requirements-full.txt
  uvicorn app.main:app --reload

Frontend local:

  cd frontend
  npm ci
  npm start