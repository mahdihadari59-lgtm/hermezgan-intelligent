from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_knowledge_provider_search_smoke(db_path):
    from app.providers.knowledge_provider import KnowledgeProvider

    provider = KnowledgeProvider(str(db_path))
    results = await provider.search("بندرعباس", limit=5)
    assert isinstance(results, list)
    assert len(results) > 0
