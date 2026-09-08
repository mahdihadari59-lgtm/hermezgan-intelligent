from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_search_pipeline_answer_smoke(db_path):
    from app.providers.knowledge_provider import KnowledgeProvider
    from app.providers.graph_provider import GraphProvider
    from app.providers.vector_provider import VectorProvider
    from app.pipelines.search_pipeline import SearchPipeline

    knowledge = KnowledgeProvider(str(db_path))
    graph = GraphProvider(str(db_path))
    vector = VectorProvider(str(db_path))
    pipeline = SearchPipeline(knowledge, graph, vector)

    result = await pipeline.answer("بندرعباس کجاست؟", limit=5)
    assert isinstance(result, dict)
    assert "answer" in result
    assert "results" in result
