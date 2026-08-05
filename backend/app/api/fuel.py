"""api/fuel.py — fuel station resource."""
from api.base import ResourceAPI


class FuelAPI(ResourceAPI):
    table = "fuel_stations"
    fields = {
        "name": {"type": "str", "required": True},
        "lat": {"type": "float", "required": True},
        "lng": {"type": "float", "required": True},
        "gasoline": {"type": "bool", "required": False, "default": True},
        "cng": {"type": "bool", "required": False, "default": False},
        "diesel": {"type": "bool", "required": False, "default": False},
        "hours": {"type": "str", "required": False},
    }
