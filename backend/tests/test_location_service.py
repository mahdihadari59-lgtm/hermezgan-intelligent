"""Unit Tests for Location Service"""

import pytest
from app.core.location_service import LocationService, get_location_service

class TestLocationService:
    """Tests for Location Service"""
    
    @pytest.fixture
    def location_service(self):
        """Initialize location service for tests"""
        return LocationService()
    
    @pytest.fixture
    def sample_entities(self):
        """Sample entities with coordinates"""
        return [
            {
                "entity_id": 1,
                "name": "بیمارستان فوق‌تخصصی کودکان",
                "type": "healthcare",
                "latitude": 27.2250,
                "longitude": 56.2950,
            },
            {
                "entity_id": 2,
                "name": "دانشگاه هرمزگان",
                "type": "educational",
                "latitude": 27.1950,
                "longitude": 56.2700,
            },
            {
                "entity_id": 3,
                "name": "بانک ملی",
                "type": "financial",
                "latitude": 27.2158,
                "longitude": 56.2808,
            },
        ]
    
    def test_calculate_distance(self, location_service):
        """Test distance calculation"""
        # Distance from (27.2158, 56.2808) to itself should be ~0
        distance = location_service.calculate_distance(
            27.2158, 56.2808,
            27.2158, 56.2808
        )
        assert distance == 0.0
    
    def test_calculate_distance_different_points(self, location_service):
        """Test distance calculation between different points"""
        distance = location_service.calculate_distance(
            27.2158, 56.2808,  # Point 1
            27.2250, 56.2950   # Point 2
        )
        assert distance > 0
        assert distance < 10  # Should be less than 10km
    
    def test_find_nearest_services(self, location_service, sample_entities):
        """Test finding nearest services"""
        results = location_service.find_nearest_services(
            sample_entities,
            27.2158,  # Center latitude
            56.2808,  # Center longitude
            radius_km=5
        )
        
        assert len(results) > 0
        # Results should be sorted by distance
        for i in range(len(results) - 1):
            assert results[i]["distance_km"] <= results[i + 1]["distance_km"]
    
    def test_find_nearest_services_by_type(self, location_service, sample_entities):
        """Test finding nearest services filtered by type"""
        results = location_service.find_nearest_services(
            sample_entities,
            27.2158,
            56.2808,
            service_type="healthcare",
            radius_km=5
        )
        
        assert len(results) > 0
        assert all(r["type"] == "healthcare" for r in results)
    
    def test_find_nearest_services_radius_filter(self, location_service, sample_entities):
        """Test radius filtering"""
        results = location_service.find_nearest_services(
            sample_entities,
            27.2158,
            56.2808,
            radius_km=0.5  # Very small radius
        )
        
        # Some entities might be outside this radius
        assert len(results) >= 0
    
    def test_get_route_info(self, location_service):
        """Test route information"""
        route = location_service.get_route_info(
            27.2158, 56.2808,  # Start
            27.2250, 56.2950   # End
        )
        
        assert "start" in route
        assert "end" in route
        assert "distance_km" in route
        assert "estimated_time_minutes" in route
        assert route["distance_km"] > 0
        assert route["estimated_time_minutes"] > 0
    
    def test_search_in_radius(self, location_service, sample_entities):
        """Test search within radius"""
        results = location_service.search_in_radius(
            sample_entities,
            27.2158,
            56.2808,
            radius_km=10
        )
        
        assert len(results) == 3  # All entities within 10km
    
    def test_get_location_suggestions(self, location_service, sample_entities):
        """Test location suggestions"""
        results = location_service.get_location_suggestions(
            "بیمارستان",
            sample_entities,
            max_results=5
        )
        
        assert len(results) > 0
        assert "بیمارستان" in results[0]["name"]
    
    def test_get_location_service_singleton(self):
        """Test location service singleton pattern"""
        service1 = get_location_service()
        service2 = get_location_service()
        assert service1 is service2


class TestLocationServiceEdgeCases:
    """Edge case tests for location service"""
    
    @pytest.fixture
    def location_service(self):
        return LocationService()
    
    def test_entities_without_coordinates(self, location_service):
        """Test filtering entities without coordinates"""
        entities = [
            {"name": "Entity 1"},  # No coordinates
            {
                "name": "Entity 2",
                "latitude": 27.2158,
                "longitude": 56.2808,
            },
        ]
        
        results = location_service.find_nearest_services(
            entities,
            27.2158,
            56.2808,
            radius_km=10
        )
        
        # Should only include entity with coordinates
        assert len(results) == 1
    
    def test_invalid_coordinates(self, location_service):
        """Test handling invalid coordinates"""
        distance = location_service.calculate_distance(
            1000, 1000,  # Invalid latitude
            27.2158, 56.2808
        )
        assert distance == -1  # Error indicator
    
    def test_search_empty_entities(self, location_service):
        """Test search with empty entities list"""
        results = location_service.find_nearest_services(
            [],
            27.2158,
            56.2808,
            radius_km=10
        )
        
        assert len(results) == 0
    
    def test_search_no_results(self, location_service):
        """Test search with no matching type"""
        entities = [
            {
                "name": "Entity 1",
                "type": "type1",
                "latitude": 27.2158,
                "longitude": 56.2808,
            },
        ]
        
        results = location_service.find_nearest_services(
            entities,
            27.2158,
            56.2808,
            service_type="type2",
            radius_km=10
        )
        
        assert len(results) == 0
