"""api/poi.py — generic POI resource (any category) backed by the shared
`pois` table. Used for bulk OSM import (mosque, school, park, market,
police, pharmacy, museum, ...) and any future ad-hoc category that doesn't
warrant its own dedicated table + frontend layer.

Unlike TourismAPI, this has no `fixed_filters` -- it's intentionally the
"anything goes" resource. If a category later needs its own validation
rules (e.g. a `police` resource with a `phone` field), give it its own
ResourceAPI subclass the same way hospitals/fuel/cameras/traffic did.
"""
from api.base import ResourceAPI


class PoiAPI(ResourceAPI):
    table = "pois"
    fields = {
        "category": {"type": "str", "required": True},
        "name": {"type": "str", "required": True},
        "lat": {"type": "float", "required": True},
        "lng": {"type": "float", "required": True},
        "description": {"type": "str", "required": False},
        "tags": {"type": "json", "required": False, "default": [], "column": "tags_json"},
    }
