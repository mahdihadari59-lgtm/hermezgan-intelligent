from __future__ import annotations

from typing import Any, Dict, Optional

from app.pipelines.rag_pipeline import RagPipeline


class VoicePipeline:
    def __init__(self, rag_pipeline: RagPipeline):
        self.rag_pipeline = rag_pipeline

    async def run(self, stt_text: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        return await self.rag_pipeline.run(stt_text, session_id=session_id)
