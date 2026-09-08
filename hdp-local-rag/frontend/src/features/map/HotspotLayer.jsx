import { useEffect, useState } from "react";
import { CircleMarker, Popup } from "react-leaflet";
import { hotspotsApi } from "@api/hotspots.api";
import { useMapStore } from "@stores/map.store";
import { Flame } from "lucide-react";

const hotspotColors = {
  low: "#f59e0b",
  medium: "#f97316",
  high: "#ef4444",
  critical: "#7f1d1d",
};

export function HotspotLayer() {
  const [hotspots, setHotspots] = useState([]);
  const { center } = useMapStore();

  useEffect(() => {
    async function load() {
      try {
        const data = await hotspotsApi.list({
          lat: center.lat,
          lng: center.lng,
          radius: 20000,
        });
        setHotspots(data || []);
      } catch (e) {
        console.error("Hotspot load error:", e);
      }
    }
    load();
  }, [center]);

  return (
    <>
      {hotspots.map((hotspot) => (
        <CircleMarker
          key={hotspot.id}
          center={[hotspot.lat, hotspot.lng]}
          radius={hotspot.radius ? hotspot.radius / 100 : 20}
          fillColor={hotspotColors[hotspot.severity] || "#f59e0b"}
          color={hotspotColors[hotspot.severity] || "#f59e0b"}
          fillOpacity={0.3}
          weight={2}
        >
          <Popup>
            <div className="text-right text-sm min-w-[150px]">
              <div className="flex items-center gap-2 mb-1">
                <Flame className="h-4 w-4 text-red-500" />
                <span className="font-bold">{hotspot.name || "نقطه داغ"}</span>
              </div>
              <p className="text-xs text-muted-foreground">
                شدت: {hotspot.severity}
              </p>
              <p className="text-xs text-muted-foreground">
                تعداد حادثه: {hotspot.incident_count || 0}
              </p>
            </div>
          </Popup>
        </CircleMarker>
      ))}
    </>
  );
}
