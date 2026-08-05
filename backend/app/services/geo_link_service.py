from __future__ import annotations

from typing import Any

from app.repositories.geo_repository import enrich_payload


class GeoLinkService:
    @staticmethod
    def enrich(payload: Any) -> Any:
        return enrich_payload(payload)


def enrich_geo(payload: Any) -> Any:
    return GeoLinkService.enrich(payload)
