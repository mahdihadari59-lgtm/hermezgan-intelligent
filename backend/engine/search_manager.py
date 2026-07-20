#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HDP Search Manager v4.0

Thin Orchestrator

SearchManager
      ↓
SearchPipeline

Author: Mahdi Hadari
"""

import logging

from engine.config import DATABASE_PATH
from engine.engine_manager import EngineManager
from engine.pipeline import SearchPipeline

logger = logging.getLogger(__name__)


class SearchManager:
    """
    Thin Search Orchestrator

    تمام منطق جستجو داخل Pipeline است.
    """

    def __init__(self, db_path=None):

        self.db_path = db_path or str(DATABASE_PATH)
        self.engine = EngineManager(self.db_path)
        self.pipeline = SearchPipeline(self.engine)

        logger.info("SearchManager Ready")

    def search(
        self,
        query,
        context=None
    ):
        """
        Execute search.

        Args:
            query: user query
            context: optional context

        Returns:
            ranked results
        """

        context = context or {}

        return self.pipeline.run(
            query,
            context
        )

    def close(self):

        if hasattr(self.pipeline, "close"):
            self.pipeline.close()

        if hasattr(self.engine, "close"):
            self.engine.close()

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type,
        exc_val,
        exc_tb
    ):
        self.close()
        return False


if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

    try:
        with SearchManager() as manager:

            response = manager.search("بندرعباس")

            print("=" * 60)
            print(response.get("answer", "پاسخی تولید نشد"))
            print("=" * 60)

            print("\nنتایج مرتبط:\n")

            for i, r in enumerate(response.get("items", [])[:5], 1):
                print(f"{i}. {r.get('title', '-')}")
                print(f"   Score : {r.get('score', 0):.2f}")
                print(f"   Source: {r.get('source', '-')}")
                print()

    except Exception:
        logger.exception("Search failed")
