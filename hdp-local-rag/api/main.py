import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.core.orchestrator import HdpOrchestrator

app = FastAPI(title="HDP Local RAG API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

orch = HdpOrchestrator()

class QueryRequest(BaseModel):
    query: str
    ai_mode: str = "auto"

@app.post("/ask")
async def ask(req: QueryRequest):
    result = await orch.process(req.query, req.ai_mode)
    return result

@app.get("/health")
def health():
    return {"status": "ok", "service": "hdp-local-rag"}

@app.get("/stats")
def stats():
    from src.knowledge.db_connector import db
    return db.get_table_counts()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
