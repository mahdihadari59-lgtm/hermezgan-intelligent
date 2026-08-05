from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_chat_service_process_message_smoke(chat_service):
    result = await chat_service.process_message("سلام", "test-user")
    assert isinstance(result, dict)
    assert "response" in result
    assert "intent" in result
    assert "retrieved_documents" in result


@pytest.mark.asyncio
async def test_chat_service_location_smoke(chat_service):
    result = await chat_service.process_message(
        "بندرعباس کجاست؟",
        "test-user",
        latitude=27.2158,
        longitude=56.2808,
    )
    assert isinstance(result, dict)
    assert "response" in result
