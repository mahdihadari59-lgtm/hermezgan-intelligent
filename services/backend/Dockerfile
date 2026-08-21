name=services/backend/Dockerfile
# Backend Dockerfile (FastAPI)

FROM python:3.11-slim AS base

# system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only requirements first for caching
COPY backend/requirements-full.txt ./

RUN python -m pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements-full.txt

# Copy app
COPY backend/ ./backend
WORKDIR /app/backend

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]