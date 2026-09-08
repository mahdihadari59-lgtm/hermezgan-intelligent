from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_gateway_handle_message_smoke(gateway):
    result = await gateway.handle_message("بندرعباس کجاست؟", session_id="test", user_id="test")
    assert isinstance(result, dict)
    assert "response" in result
    assert "knowledge" in result
    assert "retrieved_documents" in result
