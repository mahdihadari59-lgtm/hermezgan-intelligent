import io
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from geo.migrate import migrate
import geo.server as srv

SCHEMA = os.path.join(os.path.dirname(__file__), "..", "geo", "schema.sql")


class _FakeWfile(io.BytesIO):
    def close(self):
        pass


class _FakeHandler(srv.Handler):
    def __init__(self, path, headers=None):
        self.path = path
        self.headers = headers or {}
        self.wfile = _FakeWfile()
        self.rfile = io.BytesIO(b"")
        self._status = None

    def send_response(self, code):
        self._status = code

    def send_header(self, *a):
        pass

    def end_headers(self):
        pass


def call(method, path, body=None, headers=None):
    h = _FakeHandler(path, headers=headers or {})
    if body is not None:
        raw = json.dumps(body).encode("utf-8")
        h.rfile = io.BytesIO(raw)
        h.headers["Content-Length"] = str(len(raw))
    getattr(h, f"do_{method}")()
    out = h.wfile.getvalue()
    return h._status, (json.loads(out) if out else None)


class ServerRoutingTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()
        migrate(self.tmp.name, SCHEMA)
        srv.DB_PATH = self.tmp.name
        srv.API_KEY = None
        srv.ALLOWED_ORIGIN = None

    def tearDown(self):
        os.unlink(self.tmp.name)

    def test_unknown_resource_404(self):
        status, _ = call("GET", "/api/v1/map/spaceships")
        self.assertEqual(status, 404)

    def test_create_then_bbox_list(self):
        status, body = call("POST", "/api/v1/map/hospitals",
                             {"name": "H", "lat": 27.2, "lng": 56.2, "type": "general"})
        self.assertEqual(status, 201)
        self.assertIn("id", body)

        status, rows = call("GET", "/api/v1/map/hospitals?north=27.3&south=27.1&east=56.3&west=56.1")
        self.assertEqual(status, 200)
        self.assertEqual(len(rows), 1)

    def test_create_validation_error_returns_400(self):
        status, body = call("POST", "/api/v1/map/hospitals", {"lat": 27.2, "lng": 56.2, "type": "general"})
        self.assertEqual(status, 400)
        self.assertIn("error", body)

    def test_get_update_delete_cycle(self):
        _, created = call("POST", "/api/v1/map/tourism", {"name": "P", "lat": 27.1, "lng": 56.3})
        obj_id = created["id"]

        status, row = call("GET", f"/api/v1/map/tourism/{obj_id}")
        self.assertEqual(status, 200)
        self.assertEqual(row["name"], "P")

        status, _ = call("PUT", f"/api/v1/map/tourism/{obj_id}", {"description": "d"})
        self.assertEqual(status, 200)

        status, row = call("GET", f"/api/v1/map/tourism/{obj_id}")
        self.assertEqual(row["description"], "d")

        status, _ = call("DELETE", f"/api/v1/map/tourism/{obj_id}")
        self.assertEqual(status, 200)

        status, _ = call("GET", f"/api/v1/map/tourism/{obj_id}")
        self.assertEqual(status, 404)

    def test_camera_report_action(self):
        _, created = call("POST", "/api/v1/map/cameras",
                           {"code": "c1", "name": "Cam", "lat": 1, "lng": 1, "status": "active"})
        cam_id = created["id"]
        status, body = call("POST", f"/api/v1/map/cameras/{cam_id}/report", {"note": "broken"})
        self.assertEqual(status, 201)
        self.assertEqual(body["camera_id"], cam_id)

    def test_nearby_query(self):
        call("POST", "/api/v1/map/fuel", {"name": "F", "lat": 27.2158, "lng": 56.2808})
        status, rows = call("GET", "/api/v1/map/fuel?lat=27.2158&lng=56.2808&radius_km=1")
        self.assertEqual(status, 200)
        self.assertEqual(len(rows), 1)

    def test_auth_required_when_api_key_set(self):
        srv.API_KEY = "secret"
        status, _ = call("GET", "/api/v1/map/traffic")
        self.assertEqual(status, 401)
        status, _ = call("GET", "/api/v1/map/traffic", headers={"X-API-Key": "secret"})
        self.assertEqual(status, 200)
        srv.API_KEY = None

    def test_bad_json_body_returns_400(self):
        h = _FakeHandler("/api/v1/map/hospitals")
        h.rfile = io.BytesIO(b"{not valid json")
        h.headers["Content-Length"] = "15"
        h.do_POST()
        self.assertEqual(h._status, 400)


if __name__ == "__main__":
    unittest.main()
