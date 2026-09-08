import { useEffect } from "react";
import { Polyline } from "react-leaflet";
import { useMapStore } from "@stores/map.store";

export function RouteLayer() {
  const { route } = useMapStore();

  if (!route || !route.coordinates) return null;

  return (
    <Polyline
      positions={route.coordinates}
      color="#0d9488"
      weight={5}
      opacity={0.8}
      dashArray="10, 5"
    />
  );
}
