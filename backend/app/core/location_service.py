"""Location Services - GPS, Routing, and Nearest Services"""

import math
from typing import List, Tuple, Dict, Optional
from geopy.distance import geodesic
from loguru import logger

class LocationService:
    """Location Services for GPS and Routing"""
    
    # Bandar Abbas center coordinates
    CITY_CENTER = (27.2158, 56.2808)
    SEARCH_RADIUS_KM = 20  # Default search radius
    
    def __init__(self):
        """Initialize Location Service"""
        logger.info("🚀 Initializing Location Service...")
        self.city_center = self.CITY_CENTER
        logger.info(f"✅ Location Service initialized. City center: {self.city_center}")
    
    def calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two coordinates in km"""
        try:
            point1 = (lat1, lng1)
            point2 = (lat2, lng2)
            distance = geodesic(point1, point2).kilometers
            return round(distance, 2)
        except Exception as e:
            logger.error(f"Distance calculation error: {e}")
            return -1
    
    def find_nearest_services(
        self,
        entities: List[Dict],
        latitude: float,
        longitude: float,
        service_type: Optional[str] = None,
        radius_km: float = 5
    ) -> List[Dict]:
        """Find nearest services within radius"""
        logger.info(
            f"🔍 Finding nearest {service_type or 'all'} services within {radius_km}km "
            f"of ({latitude}, {longitude})"
        )
        
        nearby_services = []
        
        for entity in entities:
            # Skip entities without coordinates
            if not entity.get("latitude") or not entity.get("longitude"):
                continue
            
            # Filter by service type if specified
            if service_type and entity.get("type") != service_type:
                continue
            
            # Calculate distance
            distance = self.calculate_distance(
                latitude,
                longitude,
                entity["latitude"],
                entity["longitude"]
            )
            
            # Add if within radius
            if distance <= radius_km:
                nearby_services.append({
                    **entity,
                    "distance_km": distance,
                })
        
        # Sort by distance
        nearby_services.sort(key=lambda x: x["distance_km"])
        
        logger.info(f"✅ Found {len(nearby_services)} nearby services")
        return nearby_services
    
    def get_route_info(
        self,
        start_lat: float,
        start_lng: float,
        end_lat: float,
        end_lng: float,
        entity_details: Dict = None
    ) -> Dict:
        """Get route information between two points"""
        logger.info(f"🗺️ Calculating route from ({start_lat}, {start_lng}) to ({end_lat}, {end_lng})")
        
        distance = self.calculate_distance(start_lat, start_lng, end_lat, end_lng)
        
        # Estimate time (assuming 40 km/h average speed in city)
        estimated_time_minutes = int((distance / 40) * 60)
        
        route_info = {
            "start": {
                "latitude": start_lat,
                "longitude": start_lng,
            },
            "end": {
                "latitude": end_lat,
                "longitude": end_lng,
            },
            "distance_km": distance,
            "estimated_time_minutes": estimated_time_minutes,
            "destination_details": entity_details,
        }
        
        logger.info(f"✅ Route calculated: {distance}km, ~{estimated_time_minutes} minutes")
        return route_info
    
    def search_in_radius(
        self,
        entities: List[Dict],
        center_lat: float,
        center_lng: float,
        radius_km: float = 10,
        entity_type: Optional[str] = None
    ) -> List[Dict]:
        """Search entities within a geographic radius"""
        logger.info(
            f"🔎 Searching {entity_type or 'all entities'} "
            f"within {radius_km}km of ({center_lat}, {center_lng})"
        )
        
        results = []
        
        for entity in entities:
            if not entity.get("latitude") or not entity.get("longitude"):
                continue
            
            if entity_type and entity.get("type") != entity_type:
                continue
            
            distance = self.calculate_distance(
                center_lat,
                center_lng,
                entity["latitude"],
                entity["longitude"]
            )
            
            if distance <= radius_km:
                results.append({
                    **entity,
                    "distance_km": distance,
                })
        
        results.sort(key=lambda x: x["distance_km"])
        logger.info(f"✅ Found {len(results)} entities")
        return results
    
    def get_location_suggestions(
        self,
        query: str,
        entities: List[Dict],
        max_results: int = 5
    ) -> List[Dict]:
        """Get location suggestions based on text query"""
        logger.info(f"💡 Getting location suggestions for: {query}")
        
        query_lower = query.lower()
        suggestions = []
        
        for entity in entities:
            name = entity.get("name", "").lower()
            description = entity.get("description", "").lower()
            
            # Simple substring matching
            if query_lower in name or query_lower in description:
                suggestions.append(entity)
        
        logger.info(f"✅ Found {len(suggestions)} suggestions")
        return suggestions[:max_results]


# Global Location Service Instance
location_service = None

def get_location_service() -> LocationService:
    """Get or initialize location service"""
    global location_service
    if location_service is None:
        location_service = LocationService()
    return location_service
