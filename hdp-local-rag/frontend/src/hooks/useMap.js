import { useCallback, useEffect, useRef } from "react";
import { useMapStore } from "@stores/map.store";
import { locationsApi } from "@api/locations.api";
import { poisApi } from "@api/pois.api";

export function useMap() {
  const mapRef = useRef(null);
  const store = useMapStore();

  const flyTo = useCallback((lat, lng, zoom = 15) => {
    if (mapRef.current) {
      mapRef.current.flyTo([lat, lng], zoom, { duration: 1.5 });
    }
    store.setCenter({ lat, lng });
  }, [store]);

  const locateUser = useCallback(async () => {
    if (!navigator.geolocation) return;

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        store.setUserLocation({ lat: latitude, lng: longitude });
        flyTo(latitude, longitude, 16);
      },
      (error) => {
        console.error("Geolocation error:", error);
      }
    );
  }, [store, flyTo]);

  const searchLocation = useCallback(async (query) => {
    try {
      const results = await locationsApi.search({ q: query });
      return results;
    } catch (error) {
      console.error("Search error:", error);
      return [];
    }
  }, []);

  const getRoute = useCallback(async (from, to) => {
    try {
      const route = await locationsApi.route({
        from_lat: from.lat,
        from_lng: from.lng,
        to_lat: to.lat,
        to_lng: to.lng,
      });
      store.setRoute(route);
      return route;
    } catch (error) {
      console.error("Route error:", error);
      return null;
    }
  }, [store]);

  const getNearbyPOIs = useCallback(async (lat, lng, radius = 5000) => {
    try {
      const pois = await poisApi.nearby({ lat, lng, radius });
      return pois;
    } catch (error) {
      console.error("POI error:", error);
      return [];
    }
  }, []);

  return {
    mapRef,
    ...store,
    flyTo,
    locateUser,
    searchLocation,
    getRoute,
    getNearbyPOIs,
  };
}
