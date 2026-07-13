"""api/tourism.py — tourism site resource (backed by the generic `pois` table,
filtered to category='attraction').

NOTE: the real OSM/Neshan scrape (see geo/import_osm_geodata.py) tags
tourism sites as 'attraction', not 'tourism' -- there is no 'tourism' value
anywhere in the source taxonomy. This resource follows OSM's naming rather
than inventing a category the data will never actually use; the route stays
"/api/v1/map/tourism" for frontend compatibility, it's just the underlying
filter value that matches reality. Related categories the scrape keeps
separate (museum, beach, island) are reachable via the generic /poi route
if you want them folded in later.
"""
from app.api.base import ResourceAPI


class TourismAPI(ResourceAPI):
    table = "pois"
    # `pois` is shared with the generic PoiAPI (used for bulk OSM import
    # covering mosques, schools, parks, etc.) -- fixed_filters keeps this
    # endpoint scoped to tourism sites only, both on read and on write.
    fixed_filters = {"category": "attraction"}
    fields = {
        "category": {"type": "str", "required": False, "default": "attraction"},
        "name": {"type": "str", "required": True},
        "lat": {"type": "float", "required": True},
        "lng": {"type": "float", "required": True},
        "description": {"type": "str", "required": False},
        "tags": {"type": "json", "required": False, "default": [], "column": "tags_json"},
    }
