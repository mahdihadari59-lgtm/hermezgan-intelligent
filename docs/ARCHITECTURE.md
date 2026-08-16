name=docs/ARCHITECTURE.md
# Architecture summary for release

This document summarizes the runtime architecture for Hermezgan Intelligent platform.

- API: FastAPI backend (backend/app)
- Search Engine: hybrid engine in backend/engine (BM25+/TF-IDF/embedding)
- Knowledge: ingestion scripts in scripts/ and data/knowledge_base.json (externalized in production)
- Language engine: bandari-engine (Node)
- Frontend: React app (frontend/)
- Orchestration: docker-compose (infra/docker-compose.*.yml) and optional Kubernetes manifests in infra/k8s/

Deployment recommendations:
- Use managed vector DB for scale (Weaviate/Pinecone) and Redis Stack for caching/local dev
- Containerize each service and push to GHCR
- Use secrets in GitHub Actions and runtime secret manager