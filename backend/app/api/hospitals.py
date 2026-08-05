"""api/hospitals.py — hospital resource."""
from api.base import ResourceAPI


class HospitalAPI(ResourceAPI):
    table = "hospitals"
    fields = {
        "name": {"type": "str", "required": True},
        "lat": {"type": "float", "required": True},
        "lng": {"type": "float", "required": True},
        "type": {"type": "str", "required": True, "enum": {"general", "pediatric", "specialized"}},
        "beds": {"type": "int", "required": False},
        "emergency": {"type": "bool", "required": False, "default": True},
        "phone": {"type": "str", "required": False},
        "address": {"type": "str", "required": False},
    }
