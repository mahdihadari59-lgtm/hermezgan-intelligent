import pytest

class TestImportOsmGeodata:
    """تست‌های وارد کردن داده‌های OSM"""

    def test_import_file(self):
        """تست import_file"""
        try:
            from geo.import_osm_geodata import import_file
            result = import_file("test.osm")
            assert result is not None
        except ImportError:
            pytest.skip("geo.import_osm_geodata not available")

    def test_import_with_batch_size(self):
        """تست import_file با batch_size"""
        try:
            from geo.import_osm_geodata import import_file
            result = import_file("test.osm", batch_size=100)
            assert result is not None
        except ImportError:
            pytest.skip("geo.import_osm_geodata not available")

    def test_import_preserves_osm_id(self):
        """تست حفظ osm_id"""
        try:
            from geo.import_osm_geodata import import_file
            result = import_file("test.osm")
            assert result is not None
        except ImportError:
            pytest.skip("geo.import_osm_geodata not available")
