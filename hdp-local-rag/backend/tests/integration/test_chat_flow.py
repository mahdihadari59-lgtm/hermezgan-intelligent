from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_full_chat_flow_smoke(chat_service):
    result = await chat_service.process_message("بندرعباس کجاست؟", "test-user")
    assert isinstance(result, dict)
    assert result.get("response")
