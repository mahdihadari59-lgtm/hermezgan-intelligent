from __future__ import annotations

import asyncio
import json
import os
import urllib.parse
import urllib.request
from typing import Any, Dict

from . import BaseProvider


class WeatherProvider(BaseProvider):
    def __init__(self, city: str = "Bandar Abbas"):
        super().__init__()
        self.city = city

    def _fallback(self) -> Dict[str, Any]:
        return {
            "city": "بندرعباس",
            "temp": 38,
            "humidity": 65,
            "wind": "شمال شرقی 12km/h",
            "tip": "کولر فراموش نشود",
            "source": "fallback",
        }

    async def get_weather(self) -> Dict[str, Any]:
        def _sync() -> Dict[str, Any]:
            api_key = os.getenv("WEATHER_API_KEY")
            if not api_key:
                return self._fallback()

            try:
                q = urllib.parse.quote(self.city)
                url = f"https://api.openweathermap.org/data/2.5/weather?q={q}&appid={api_key}&units=metric"
                with urllib.request.urlopen(url, timeout=self.timeout_seconds) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                if str(data.get("cod")) != "200":
                    return self._fallback()
                return {
                    "city": "بندرعباس",
                    "temp": round(data["main"]["temp"]),
                    "humidity": data["main"]["humidity"],
                    "wind": f'{round(data["wind"]["speed"])} km/h',
                    "tip": "کولر فراموش نشود" if data["main"]["temp"] > 40 else "هوا مطبوع است",
                    "source": "openweather",
                }
            except Exception:
                return self._fallback()

        return await asyncio.to_thread(_sync)
