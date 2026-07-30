"""
providers/weather_provider.py

External weather lookup for Hormozgan cities. Since HDP is offline-first,
this provider is expected to fail closed (circuit opens quickly, gateway
falls back to "no live weather" rather than blocking the whole response).

Swap `base_url`/`api_key_env` for whatever provider you settle on
(e.g. an Iranian met service, or a self-hosted cache synced when online).
"""

from __future__ import annotations

import os

from . import BaseProvider, ProviderError


class WeatherProvider(BaseProvider):
    name = "weather"

    def __init__(self, base_url: str | None = None, api_key_env: str = "HDP_WEATHER_API_KEY", timeout: float = 3.0):
        # Short timeout + low failure threshold: this is a "nice to have"
        # enrichment, never a blocking dependency for chat responses.
        super().__init__(timeout=timeout, failure_threshold=2, recovery_timeout=60.0)
        self.base_url = (base_url or os.environ.get("HDP_WEATHER_BASE_URL", "")).rstrip("/")
        self.api_key = os.environ.get(api_key_env, "")

    async def _execute(self, payload: dict) -> dict:
        if payload.get("__health__"):
            if not self.base_url:
                raise ProviderError("weather: no base_url configured")
            return {"ok": True}

        city = payload.get("city")
        if not city:
            raise ProviderError("weather: 'city' is required")
        if not self.base_url or not self.api_key:
            raise ProviderError("weather: not configured (missing base_url or api key)")

        url = f"{self.base_url}/current?city={city}&key={self.api_key}"
        return await self._http_get(url)

    async def current(self, city: str) -> dict | None:
        try:
            return await self.query({"city": city})
        except ProviderError:
            # Offline-first: absence of weather data must never break a chat turn.
            return None
