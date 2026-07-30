"""
experts/tourism_expert.py

Answers tourism/attraction questions, and when the user mentions a specific
city, attaches current weather from WeatherProvider (best-effort — see
WeatherProvider's offline-first fallback).
"""

from __future__ import annotations

import re

from app.experts import BaseExpert
from app.pipelines.rag_pipeline import RAGResult
from app.providers.weather_provider import WeatherProvider

# Known Hormozgan cities/towns worth checking weather for. Extend as needed.
_KNOWN_CITIES = ["بندرعباس", "قشم", "میناب", "بستک", "بندرلنگه", "کیش", "رودان", "حاجی‌آباد"]


class TourismExpert(BaseExpert):
    domain = "tourism"
    category = "tourism"

    def __init__(self, rag, weather: WeatherProvider):
        super().__init__(rag)
        self.weather = weather

    async def enrich(self, user_text: str, result: RAGResult) -> dict:
        city = self._extract_city(user_text)
        if not city:
            return {}
        weather = await self.weather.current(city)
        return {"city": city, "weather": weather}

    def _extract_city(self, text: str) -> str | None:
        for city in _KNOWN_CITIES:
            if city in text:
                return city
        return None
