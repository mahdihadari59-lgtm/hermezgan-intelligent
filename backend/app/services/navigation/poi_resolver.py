from __future__ import annotations

import math
import os
import re
import sqlite3
from typing import Optional

from app.services.driver_assistant.models import Location, POICandidate
from app.services.driver_assistant.exceptions import DestinationNotFoundError


DEFAULT_DB = (
    "/data/data/com.termux/files/home/"
    "hormozgan_geo_project/hormozgan_data/"
    "hormozgan_master_final.db"
)


class POIResolver:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = (
            db_path
            or os.getenv("HDP_RAG_DB_PATH")
            or os.getenv("DB_PATH")
            or DEFAULT_DB
        )

    @staticmethod
    def _tokens(text: str) -> list[str]:
        values = []
        seen = set()
        for token in re.split(r"[\s،,؛;:؟?!.\-_]+", text or ""):
            token = token.strip().replace("ي", "ی").replace("ك", "ک")
            if len(token) >= 2 and token not in seen:
                values.append(token)
                seen.add(token)
        return values

    @staticmethod
    def _distance_m(a: Location, b: Location) -> float:
        r = 6371000.0
        p1 = math.radians(a.latitude)
        p2 = math.radians(b.latitude)
        dp = math.radians(b.latitude - a.latitude)
        dl = math.radians(b.longitude - a.longitude)

        x = (
            math.sin(dp / 2) ** 2
            + math.cos(p1)
            * math.cos(p2)
            * math.sin(dl / 2) ** 2
        )

        return 2 * r * math.asin(math.sqrt(x))

    async def search(
        self,
        query: str,
        near_location: Optional[Location] = None,
        category: Optional[str] = None,
        limit: int = 10,
    ) -> list[POICandidate]:
        tokens = self._tokens(query)
        if not tokens:
            raise DestinationNotFoundError("نام مقصد خالی است")

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row

        try:
            rows = conn.execute(
                """
                SELECT name, lat, lon, cat, subcat
                FROM poi_unified
                WHERE name IS NOT NULL
                  AND lat IS NOT NULL
                  AND lon IS NOT NULL
                LIMIT 5000
                """
            ).fetchall()

            candidates: list[POICandidate] = []

            for row in rows:
                name = str(row["name"] or "")
                normalized = name.replace("ي", "ی").replace("ك", "ک")

                hit_count = sum(
                    1 for token in tokens
                    if token.lower() in normalized.lower()
                )

                if hit_count == 0:
                    continue

                token_score = hit_count / len(tokens)
                exact_bonus = 0.35 if normalized.lower() == query.lower() else 0.0

                distance_bonus = 0.0
                distance_m = None

                if near_location:
                    distance_m = self._distance_m(
                        near_location,
                        Location(
                            float(row["lat"]),
                            float(row["lon"]),
                        ),
                    )
                    distance_bonus = max(
                        0.0,
                        0.25 * (1.0 - min(distance_m, 20000.0) / 20000.0),
                    )

                category_bonus = (
                    0.10
                    if category and str(row["cat"] or "").lower() == category.lower()
                    else 0.0
                )

                score = token_score + exact_bonus + distance_bonus + category_bonus

                candidates.append(
                    POICandidate(
                        name=name,
                        latitude=float(row["lat"]),
                        longitude=float(row["lon"]),
                        score=score,
                        category=row["cat"],
                        subcategory=row["subcat"],
                    )
                )

            candidates.sort(key=lambda x: x.score, reverse=True)
            return candidates[:limit]

        finally:
            conn.close()

    async def resolve_ambiguity(
        self,
        candidates: list[POICandidate],
        current_location: Optional[Location] = None,
    ) -> Optional[POICandidate]:
        if not candidates:
            return None

        if len(candidates) == 1:
            return candidates[0]

        if current_location:
            return min(
                candidates,
                key=lambda c: self._distance_m(
                    current_location,
                    c.location,
                ),
            )

        return max(candidates, key=lambda c: c.score)
