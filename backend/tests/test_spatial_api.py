import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from geo.migrate import migrate
from geo.spatial_api import SpatialDB, SpatialDBError, haversine_km


SCHEMA = os.path.join(os.path.dirname(__file__), "..", "geo", "schema.sql")


class SpatialApiTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()
        migrate(self.tmp.name, SCHEMA)
        self.db = SpatialDB(self.tmp.name)

    def tearDown(self):
        self.db.close()
        os.unlink(self.tmp.name)

    def test_haversine_zero_distance(self):
        self.assertAlmostEqual(haversine_km(27.2, 56.2, 27.2, 56.2), 0.0, places=6)

    def test_insert_and_get(self):
        new_id = self.db.insert("hospitals", name="Test", lat=27.2, lng=56.2, type="general")
        row = self.db.get("hospitals", new_id)
        self.assertEqual(row["name"], "Test")
        self.assertEqual(row["type"], "general")

    def test_bbox_query_finds_point_inside(self):
        self.db.insert("cameras", code="x1", name="Cam", lat=27.20, lng=56.20, status="active")
        rows = self.db.query_bbox("cameras", north=27.30, south=27.10, east=56.30, west=56.10)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["code"], "x1")

    def test_bbox_query_excludes_point_outside(self):
        self.db.insert("cameras", code="x2", name="Cam", lat=10.0, lng=10.0, status="active")
        rows = self.db.query_bbox("cameras", north=27.30, south=27.10, east=56.30, west=56.10)
        self.assertEqual(len(rows), 0)

    def test_radius_query_distance_and_ordering(self):
        self.db.insert("fuel_stations", name="Near", lat=27.2158, lng=56.2808)
        self.db.insert("fuel_stations", name="Far", lat=27.30, lng=56.40)
        results = self.db.query_radius("fuel_stations", lat=27.2158, lng=56.2808, radius_km=5)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Near")
        self.assertAlmostEqual(results[0]["distance_km"], 0.0, places=2)

    def test_nearest_k_expands_radius_until_enough_found(self):
        # Two points close, one far (> initial 2km search radius)
        self.db.insert("hospitals", name="A", lat=27.2158, lng=56.2808, type="general")
        self.db.insert("hospitals", name="B", lat=27.2160, lng=56.2810, type="general")
        self.db.insert("hospitals", name="C", lat=27.50, lng=56.60, type="general")
        results = self.db.query_nearest("hospitals", lat=27.2158, lng=56.2808, k=3)
        self.assertEqual(len(results), 3)
        self.assertEqual([r["name"] for r in results], ["A", "B", "C"])

    def test_update_persists_and_syncs_rtree(self):
        obj_id = self.db.insert("traffic", name="Seg", lat=27.0, lng=56.0, level="light")
        self.db.update("traffic", obj_id, lat=28.0, lng=57.0, level="heavy")
        row = self.db.get("traffic", obj_id)
        self.assertEqual(row["level"], "heavy")
        self.assertEqual(row["lat"], 28.0)
        # bbox around new location should find it
        found = self.db.query_bbox("traffic", north=28.5, south=27.5, east=57.5, west=56.5)
        self.assertEqual(len(found), 1)
        # bbox around old location should not
        gone = self.db.query_bbox("traffic", north=27.5, south=26.5, east=56.5, west=55.5)
        self.assertEqual(len(gone), 0)

    def test_delete_removes_row_and_rtree_entry(self):
        obj_id = self.db.insert("hospitals", name="ToDelete", lat=27.2, lng=56.2, type="general")
        self.db.delete("hospitals", obj_id)
        self.assertIsNone(self.db.get("hospitals", obj_id))

    def test_update_missing_row_raises(self):
        with self.assertRaises(SpatialDBError):
            self.db.update("hospitals", 9999, name="Nope")

    def test_delete_missing_row_raises(self):
        with self.assertRaises(SpatialDBError):
            self.db.delete("hospitals", 9999)

    def test_json_field_roundtrip(self):
        obj_id = self.db.insert(
            "cameras", code="x3", name="Cam", lat=27.2, lng=56.2, status="active",
            types_json='["speed", "plate"]',
        )
        row = self.db.get("cameras", obj_id)
        self.assertEqual(row["types"], ["speed", "plate"])

    def test_boolean_field_roundtrip(self):
        obj_id = self.db.insert(
            "fuel_stations", name="F", lat=27.2, lng=56.2, gasoline=1, cng=0, diesel=1,
        )
        row = self.db.get("fuel_stations", obj_id)
        self.assertIs(row["gasoline"], True)
        self.assertIs(row["cng"], False)


if __name__ == "__main__":
    unittest.main()
