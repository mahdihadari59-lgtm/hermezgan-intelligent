import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from geo.migrate import migrate
from geo.spatial_api import SpatialDB
from api.base import ValidationError, NotFoundError
from api.traffic import TrafficAPI
from api.cameras import CameraAPI
from api.hospitals import HospitalAPI
from api.fuel import FuelAPI
from api.tourism import TourismAPI
from api.poi import PoiAPI

SCHEMA = os.path.join(os.path.dirname(__file__), "..", "geo", "schema.sql")


class ResourceApiTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()
        migrate(self.tmp.name, SCHEMA)
        self.db = SpatialDB(self.tmp.name)

    def tearDown(self):
        self.db.close()
        os.unlink(self.tmp.name)

    # ── validation ───────────────────────────────────────────────────
    def test_unknown_field_rejected(self):
        with self.assertRaises(ValidationError):
            TrafficAPI.validate({"name": "x", "lat": 1, "lng": 1, "level": "light", "nope": 1})

    def test_missing_required_field_rejected(self):
        with self.assertRaises(ValidationError):
            TrafficAPI.validate({"lat": 1, "lng": 1, "level": "light"})

    def test_enum_violation_rejected(self):
        with self.assertRaises(ValidationError):
            TrafficAPI.validate({"name": "x", "lat": 1, "lng": 1, "level": "extreme"})

    def test_type_coercion_string_to_float(self):
        cleaned = TrafficAPI.validate({"name": "x", "lat": "27.2", "lng": "56.2", "level": "light"})
        self.assertEqual(cleaned["lat"], 27.2)
        self.assertIsInstance(cleaned["lat"], float)

    def test_bad_numeric_value_rejected(self):
        with self.assertRaises(ValidationError):
            TrafficAPI.validate({"name": "x", "lat": "not-a-number", "lng": 1, "level": "light"})

    def test_defaults_applied_on_full_validate(self):
        cleaned = FuelAPI.validate({"name": "F", "lat": 1, "lng": 1})
        self.assertEqual(cleaned["gasoline"], True)
        self.assertEqual(cleaned["cng"], False)

    def test_partial_validate_skips_missing_optional_fields(self):
        cleaned = HospitalAPI.validate({"beds": 10}, partial=True)
        self.assertEqual(cleaned, {"beds": 10})

    def test_json_field_stays_as_list_after_validate(self):
        cleaned = CameraAPI.validate(
            {"code": "c1", "name": "Cam", "lat": 1, "lng": 1, "status": "active", "types": ["speed"]}
        )
        self.assertEqual(cleaned["types"], ["speed"])

    # ── create/get/update/delete through the resource layer ───────────
    def test_full_crud_cycle(self):
        new_id = TourismAPI.create(self.db, {"name": "Spot", "lat": 27.1, "lng": 56.3})
        row = TourismAPI.get(self.db, new_id)
        self.assertEqual(row["name"], "Spot")
        self.assertEqual(row["category"], "attraction")  # default applied (matches OSM's real taxonomy)

        TourismAPI.update(self.db, new_id, {"description": "nice place"})
        row = TourismAPI.get(self.db, new_id)
        self.assertEqual(row["description"], "nice place")

        TourismAPI.delete(self.db, new_id)
        with self.assertRaises(NotFoundError):
            TourismAPI.get(self.db, new_id)

    def test_update_with_no_fields_rejected(self):
        new_id = HospitalAPI.create(self.db, {"name": "H", "lat": 1, "lng": 1, "type": "general"})
        with self.assertRaises(ValidationError):
            HospitalAPI.update(self.db, new_id, {})

    def test_update_nonexistent_raises_not_found(self):
        with self.assertRaises(NotFoundError):
            HospitalAPI.update(self.db, 99999, {"beds": 5})

    def test_delete_nonexistent_raises_not_found(self):
        with self.assertRaises(NotFoundError):
            HospitalAPI.delete(self.db, 99999)

    def test_fixed_filters_scopes_reads_to_own_category(self):
        # pois table shared by TourismAPI (category='attraction') and PoiAPI (any category)
        PoiAPI.create(self.db, {"category": "mosque", "name": "Mosque", "lat": 27.1, "lng": 56.1})
        TourismAPI.create(self.db, {"name": "Attraction", "lat": 27.1, "lng": 56.1})

        all_pois = PoiAPI.list_bbox(self.db, north=90, south=-90, east=180, west=-180)
        self.assertEqual(len(all_pois), 2)

        tourism_only = TourismAPI.list_bbox(self.db, north=90, south=-90, east=180, west=-180)
        self.assertEqual(len(tourism_only), 1)
        self.assertEqual(tourism_only[0]["category"], "attraction")

    def test_fixed_filters_cannot_be_overridden_on_create(self):
        new_id = TourismAPI.create(self.db, {"name": "X", "lat": 1, "lng": 1, "category": "mosque"})
        row = TourismAPI.get(self.db, new_id)
        self.assertEqual(row["category"], "attraction")  # forced, payload's 'mosque' ignored

    def test_nearby_and_bbox_via_resource(self):
        HospitalAPI.create(self.db, {"name": "H1", "lat": 27.2158, "lng": 56.2808, "type": "general"})
        bbox_rows = HospitalAPI.list_bbox(self.db, north=27.3, south=27.1, east=56.35, west=56.2)
        self.assertEqual(len(bbox_rows), 1)
        near_rows = HospitalAPI.nearby(self.db, lat=27.2158, lng=56.2808, radius_km=1)
        self.assertEqual(len(near_rows), 1)


if __name__ == "__main__":
    unittest.main()
