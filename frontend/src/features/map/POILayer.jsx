import { useEffect, useState } from "react";
import { Marker, Popup } from "react-leaflet";
import L from "leaflet";
import { useMap } from "@hooks/useMap";
import { useMapStore } from "@stores/map.store";
import { Badge } from "@components/common/Badge";

const poiIcons = {
  restaurant: "🍽️",
  hotel: "🏨",
  hospital: "🏥",
  gas_station: "⛽",
  mosque: "🕌",
  school: "🏫",
  bank: "🏦",
  shop: "🛒",
  pharmacy: "💊",
  default: "📍",
};

function createPOIIcon(type) {
  const emoji = poiIcons[type] || poiIcons.default;
  return L.divIcon({
    className: "poi-marker",
    html: `<div style="width:32px;height:32px;background:white;border:2px solid #0d9488;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:16px;box-shadow:0 2px 8px rgba(0,0,0,0.2);">${emoji}</div>`,
    iconSize: [32, 32],
    iconAnchor: [16, 16],
  });
}

export function POILayer() {
  const [pois, setPois] = useState([]);
  const { center } = useMapStore();
  const { getNearbyPOIs } = useMap();

  useEffect(() => {
    async function load() {
      const data = await getNearbyPOIs(center.lat, center.lng, 10000);
      setPois(data || []);
    }
    load();
  }, [center, getNearbyPOIs]);

  return (
    <>
      {pois.map((poi) => (
        <Marker
          key={poi.id}
          position={[poi.lat, poi.lng]}
          icon={createPOIIcon(poi.type)}
        >
          <Popup>
            <div className="text-right min-w-[180px] p-1">
              <h4 className="font-bold text-sm">{poi.name}</h4>
              <Badge variant="outline" className="mt-1 text-xs">
                {poi.type}
              </Badge>
              <p className="mt-2 text-xs text-muted-foreground">
                {poi.address}
              </p>
              {poi.phone && (
                <p className="mt-1 text-xs text-teal-600">{poi.phone}</p>
              )}
            </div>
          </Popup>
        </Marker>
      ))}
    </>
  );
}
