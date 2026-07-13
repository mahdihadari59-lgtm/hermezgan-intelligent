"""
api/base.py — shared validation + CRUD contract for HDP map resources.

Every resource module (api/traffic.py, api/cameras.py, ...) declares a
`fields` spec and gets bbox/nearby/create/update/delete for free. This is
the layer that owns:
  - required/optional fields, enums, defaults
  - JSON-field <-> DB-column renaming (`types` <-> `types_json`)
  - turning bad input into a ValidationError with a clear message

spatial_api.SpatialDB stays "dumb": it only ever sees final DB column names
and pre-serialized values.
"""
import json

from geo.spatial_api import SpatialDB


class ValidationError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class NotFoundError(Exception):
    pass


class ResourceAPI:
    table: str = None
    # name -> {"type": "str"|"float"|"int"|"bool"|"json", "required": bool,
    #          "enum": set|None, "default": Any (optional), "column": str (optional)}
    fields: dict = {}
    # Optional: {"category": "tourism"} etc. -- used by resources that share a
    # table with other resources (e.g. TourismAPI and the generic PoiAPI both
    # use `pois`). Applied as a read-side filter on every query AND forced
    # onto every write, so TourismAPI can never see or create a non-tourism row.
    fixed_filters: dict = {}

    @classmethod
    def _coerce(cls, name: str, value, spec: dict):
        kind = spec["type"]
        try:
            if kind == "str":
                v = str(value)
            elif kind == "float":
                v = float(value)
            elif kind == "int":
                v = int(value)
            elif kind == "bool":
                v = bool(value) if not isinstance(value, str) else value.lower() in ("1", "true", "yes")
            elif kind == "json":
                v = value if isinstance(value, (list, dict)) else json.loads(value)
            else:
                v = value
        except (TypeError, ValueError, json.JSONDecodeError):
            raise ValidationError(f"invalid value for '{name}': {value!r}")

        enum = spec.get("enum")
        if enum and v not in enum:
            raise ValidationError(f"'{name}' must be one of {sorted(enum)}, got {v!r}")
        return v

    @classmethod
    def validate(cls, payload: dict, partial: bool = False) -> dict:
        if not isinstance(payload, dict):
            raise ValidationError("payload must be a JSON object")

        unknown = set(payload) - set(cls.fields)
        if unknown:
            raise ValidationError(f"unknown field(s): {sorted(unknown)}")

        cleaned = {}
        for name, spec in cls.fields.items():
            if name in payload:
                cleaned[name] = cls._coerce(name, payload[name], spec)
            elif not partial:
                if "default" in spec:
                    cleaned[name] = spec["default"]
                elif spec.get("required"):
                    raise ValidationError(f"'{name}' is required")
        return cleaned

    @classmethod
    def _to_storage(cls, cleaned: dict) -> dict:
        out = {}
        for name, value in cleaned.items():
            spec = cls.fields[name]
            col = spec.get("column", name)
            out[col] = json.dumps(value, ensure_ascii=False) if spec["type"] == "json" else value
        return out

    # ── Reads ─────────────────────────────────────────────────────────
    @classmethod
    def list_bbox(cls, db: SpatialDB, north: float, south: float, east: float, west: float,
                  limit: int = 500) -> list:
        return db.query_bbox(cls.table, north=north, south=south, east=east, west=west,
                              limit=limit, where=cls.fixed_filters or None)

    @classmethod
    def nearby(cls, db: SpatialDB, lat: float, lng: float, radius_km: float = None, k: int = None) -> list:
        if k:
            # query_nearest doesn't take `where` (it expands radius internally);
            # for fixed_filters resources, over-fetch and filter, which is fine
            # at HDP's current data volumes.
            results = db.query_nearest(cls.table, lat, lng, k=k * 5 if cls.fixed_filters else k)
            if cls.fixed_filters:
                results = [r for r in results if all(r.get(k2) == v for k2, v in cls.fixed_filters.items())]
            return results[:k]
        return db.query_radius(cls.table, lat, lng, radius_km=radius_km or 5.0, where=cls.fixed_filters or None)

    @classmethod
    def get(cls, db: SpatialDB, obj_id: int) -> dict:
        row = db.get(cls.table, obj_id)
        if row is None:
            raise NotFoundError(f"{cls.table} id={obj_id} not found")
        return row

    # ── Writes ────────────────────────────────────────────────────────
    @classmethod
    def create(cls, db: SpatialDB, payload: dict) -> int:
        cleaned = cls.validate(payload, partial=False)
        cleaned.update(cls.fixed_filters)  # e.g. force category="tourism", can't be overridden
        return db.insert(cls.table, **cls._to_storage(cleaned))

    @classmethod
    def update(cls, db: SpatialDB, obj_id: int, payload: dict) -> None:
        cleaned = cls.validate(payload, partial=True)
        if not cleaned:
            raise ValidationError("no valid fields to update")
        cleaned.update(cls.fixed_filters)
        try:
            db.update(cls.table, obj_id, **cls._to_storage(cleaned))
        except Exception as e:  # spatial_api raises SpatialDBError on missing row
            if "not found" in str(e):
                raise NotFoundError(str(e)) from e
            raise

    @classmethod
    def delete(cls, db: SpatialDB, obj_id: int) -> None:
        try:
            db.delete(cls.table, obj_id)
        except Exception as e:
            if "not found" in str(e):
                raise NotFoundError(str(e)) from e
            raise
