#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from typing import Dict, Any

logger = logging.getLogger("hdp.copilot")


class CopilotGateway:

    def __init__(
        self,
        search_pipeline=None,
        hybrid_engine=None,
        llm_client=None,
        tts_client=None,
    ):
        self.search_pipeline = search_pipeline
        self.hybrid_engine = hybrid_engine
        self.llm_client = llm_client
        self.tts_client = tts_client

    async def handle_message(
        self,
        message: Dict[str, Any],
        session_id: str,
        user_id: str,
    ) -> Dict[str, Any]:

        query = message.get("content", "")
        metadata = message.get("metadata", {})
        dialect = metadata.get("dialect", "standard")
        intent = metadata.get("intent", "general")

        documents = []
        if self.search_pipeline:
            documents = await self.search_pipeline.search(
                query=query,
                dialect=dialect,
                intent=intent,
                top_k=5,
            )
        elif self.hybrid_engine:
            documents = await self.hybrid_engine.search(
                query=query,
                limit=5,
            )

        context = []
        for doc in documents:
            text = doc.get("text", "")
            source = doc.get("source", "knowledge")
            context.append(f"[{source}]\n{text}")

        rag_context = "\n\n".join(context)
        prompt = self.build_prompt(
            query=query,
            context=rag_context,
            dialect=dialect,
            intent=intent,
        )

        if self.llm_client:
            answer = await self.llm_client.generate(
                prompt=prompt,
                session_id=session_id,
            )
        else:
            answer = "LLM Client Not Configured"

        return {
            "response": answer,
            "sources": documents,
            "metadata": {
                "dialect": dialect,
                "intent": intent,
                "retrieval_count": len(documents),
                "session_id": session_id,
                "user_id": user_id,
            },
        }

    def build_prompt(self, query, context, dialect, intent):
        return f"""
شما موتور مرکزی HDP هستید.

گویش: {dialect}
هدف: {intent}

دانش بازیابی شده:
{context}

سؤال: {query}

فقط بر اساس اطلاعات بازیابی شده پاسخ بده.
اگر اطلاعات کافی نبود اعلام کن.
"""
