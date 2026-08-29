name=services/knowledge/Dockerfile
# Knowledge service Dockerfile (ingest/embeddings worker)
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements-full.txt ./
RUN python -m pip install --upgrade pip && pip install --no-cache-dir -r requirements-full.txt
COPY scripts/ ./scripts
COPY backend/app/ ./app
ENV PYTHONUNBUFFERED=1
CMD ["python", "scripts/rebuild_embeddings.py"]