import { useEffect, useRef, useMemo } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { useMapStore } from "@stores/map.store";
import { useMap as useMapData } from "@hooks/useMap";
import { POILayer } from "./POILayer";
import { TrafficLayer } from "./TrafficLayer";
import { CameraLayer } from "./CameraLayer";
import { HotspotLayer } from "./HotspotLayer";
import { RouteLayer } from "./RouteLayer";
import { MapControls } from "./MapControls";

// Fix Leaflet default icons
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";

const DefaultIcon = L.icon({
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});
L.Marker.prototype.options.icon = DefaultIcon;

function MapController() {
  const map = useMap();
  const { center, zoom } = useMapStore();

  useEffect(() => {
    map.flyTo([center.lat, center.lng], zoom, { duration: 1.5 });
  }, [center, zoom, map]);

  return null;
}

export function MapView() {
  const { layers, userLocation } = useMapStore();

  const userIcon = useMemo(
    () =>
      L.divIcon({
        className: "custom-user-marker",
        html: `<div style="width:16px;height:16px;background:#3b82f6;border:3px solid white;border-radius:50%;box-shadow:0 2px 8px rgba(0,0,0,0.3);"></div>`,
        iconSize: [16, 16],
        iconAnchor: [8, 8],
      }),
    []
  );

  return (
    <div className="relative h-[calc(100vh-4rem)] w-full">
      <MapContainer
        center={[27.1832, 56.2666]}
        zoom={13}
        className="h-full w-full"
        zoomControl={false}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <MapController />

        {/* User location */}
        {userLocation && (
          <Marker
            position={[userLocation.lat, userLocation.lng]}
            icon={userIcon}
          >
            <Popup>
              <div className="text-right text-sm">
                <p className="font-medium">موقعیت شما</p>
                <p className="text-muted-foreground text-xs">
                  {userLocation.lat.toFixed(4)}, {userLocation.lng.toFixed(4)}
                </p>
              </div>
            </Popup>
          </Marker>
        )}

        {/* Feature layers */}
        {layers.pois && <POILayer />}
        {layers.traffic && <TrafficLayer />}
        {layers.cameras && <CameraLayer />}
        {layers.hotspots && <HotspotLayer />}
        {layers.route && <RouteLayer />}
      </MapContainer>

      <MapControls />
    </div>
  );
}
