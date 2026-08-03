#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
import logging

logger = logging.getLogger("hdp.search")


class SearchPipeline:

    def __init__(self, hybrid_engine):
        self.hybrid_engine = hybrid_engine

    async def search(
        self,
        query: str,
        intent: str = "general",
        dialect: str = "standard",
        top_k: int = 5,
    ):
        logger.info(f"SearchPipeline query={query}")
        result = await self.hybrid_engine.search(
            query=query,
            intent=intent,
            dialect=dialect,
            limit=top_k,
        )
        return result
