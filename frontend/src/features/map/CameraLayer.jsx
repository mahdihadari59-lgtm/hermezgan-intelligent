import { useEffect, useState } from "react";
import { Marker, Popup } from "react-leaflet";
import L from "leaflet";
import { camerasApi } from "@api/cameras.api";
import { useMapStore } from "@stores/map.store";
import { Camera, Eye } from "lucide-react";

const cameraIcon = L.divIcon({
  className: "camera-marker",
  html: `<div style="width:28px;height:28px;background:#dc2626;border:2px solid white;border-radius:50%;display:flex;align-items:center;justify-content:center;box-shadow:0 2px 8px rgba(0,0,0,0.3);"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/><circle cx="12" cy="13" r="3"/></svg></div>`,
  iconSize: [28, 28],
  iconAnchor: [14, 14],
});

export function CameraLayer() {
  const [cameras, setCameras] = useState([]);
  const { center } = useMapStore();

  useEffect(() => {
    async function load() {
      try {
        const data = await camerasApi.nearby(center.lat, center.lng, 15000);
        setCameras(data || []);
      } catch (e) {
        console.error("Camera load error:", e);
      }
    }
    load();
  }, [center]);

  return (
    <>
      {cameras.map((camera) => (
        <Marker
          key={camera.id}
          position={[camera.lat, camera.lng]}
          icon={cameraIcon}
        >
          <Popup>
            <div className="text-right text-sm min-w-[180px]">
              <div className="flex items-center gap-2 mb-2">
                <Camera className="h-4 w-4 text-red-500" />
                <span className="font-bold">{camera.name || "دوربین ترافیکی"}</span>
              </div>
              <p className="text-xs text-muted-foreground">
                {camera.road_name || camera.location}
              </p>
              {camera.status && (
                <p className="mt-1 text-xs">
                  وضعیت: {" "}
                  <span className={camera.status === "active" ? "text-emerald-600" : "text-amber-600"}>
                    {camera.status === "active" ? "فعال" : "غیرفعال"}
                  </span>
                </p>
              )}
            </div>
          </Popup>
        </Marker>
      ))}
    </>
  );
}
