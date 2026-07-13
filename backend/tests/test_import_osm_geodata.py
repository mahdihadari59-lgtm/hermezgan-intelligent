import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from geo.migrate import migrate
from geo.spatial_api import SpatialDB
from geo.import_osm_geodata import import_file

SCHEMA = os.path.join(os.path.dirname(__file__), "..", "geo", "schema.sql")

FIXTURE = {
    "count": 6,
    "results": [
        {"id": "node_1", "cat": "hospital", "name": "بیمارستان تست", "lat": 27.2, "lon": 56.2},
        {"id": "node_2", "cat": "fuel", "name": "پمپ بنزین تست", "lat": 27.21, "lon": 56.21},
        {"id": "node_3", "cat": "mosque", "name": "مسجد تست", "lat": 27.22, "lon": 56.22},
        {"id": "node_4", "cat": "attraction", "name": "جاذبه تست", "lat": 27.23, "lon": 56.23},
        {"id": "node_5", "cat": "mosque", "name": "", "lat": 27.24, "lon": 56.24},  # empty name
        {"id": "node_6", "cat": "missing_coords", "name": "بدون مختصات", "lat": None, "lon": None},
    ],
}


class ImportOsmGeodataTestCase(unittest.TestCase):
    def setUp(self):
        self.db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_file.close()
        migrate(self.db_file.name, SCHEMA)

        self.fixture_file = tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w", encoding="utf-8")
        json.dump(FIXTURE, self.fixture_file, ensure_ascii=False)
        self.fixture_file.close()

    def tearDown(self):
        os.unlink(self.db_file.name)
        os.unlink(self.fixture_file.name)

    def test_import_routes_by_category_and_skips_missing_coords(self):
        stats = import_file(self.fixture_file.name, self.db_file.name, batch_size=2)
        # node_6 has no lat/lon -> skipped; the rest (5) imported
        self.assertEqual(stats["imported"], 5)
        self.assertEqual(stats["skipped"], 1)

        with SpatialDB(self.db_file.name) as db:
            hospitals = db.query_bbox("hospitals", north=90, south=-90, east=180, west=-180)
            fuel = db.query_bbox("fuel_stations", north=90, south=-90, east=180, west=-180)
            pois = db.query_bbox("pois", north=90, south=-90, east=180, west=-180)

        self.assertEqual(len(hospitals), 1)
        self.assertEqual(hospitals[0]["type"], "general")
        self.assertEqual(len(fuel), 1)
        self.assertEqual(len(pois), 3)  # 2 mosque + 1 attraction

        empty_name_row = next(p for p in pois if p["name"] == "بدون نام")
        self.assertEqual(empty_name_row["category"], "mosque")

    def test_osm_id_preserved_in_tags(self):
        import_file(self.fixture_file.name, self.db_file.name, batch_size=2)
        with SpatialDB(self.db_file.name) as db:
            pois = db.query_bbox("pois", north=90, south=-90, east=180, west=-180)
        attraction = next(p for p in pois if p["category"] == "attraction")
        self.assertEqual(attraction["tags"]["osm_id"], "node_4")


if __name__ == "__main__":
    unittest.main()
