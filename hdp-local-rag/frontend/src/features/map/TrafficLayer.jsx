import { useEffect, useState } from "react";
import { CircleMarker, Popup } from "react-leaflet";
import { useTraffic } from "@hooks/useTraffic";

const congestionColors = {
  low: "#22c55e",
  medium: "#f59e0b",
  high: "#f97316",
  severe: "#ef4444",
};

export function TrafficLayer() {
  const { trafficData } = useTraffic();

  return (
    <>
      {trafficData.map((road) =>
        road.coordinates?.map((coord, idx) => (
          <CircleMarker
            key={`${road.id}-${idx}`}
            center={coord}
            radius={6}
            fillColor={congestionColors[road.congestionLevel] || "#94a3b8"}
            color={congestionColors[road.congestionLevel] || "#94a3b8"}
            fillOpacity={0.6}
            weight={2}
          >
            <Popup>
              <div className="text-right text-sm min-w-[150px]">
                <p className="font-bold">{road.roadName}</p>
                <p className="text-xs text-muted-foreground mt-1">
                  سرعت: {road.averageSpeed} km/h
                </p>
                <p className="text-xs text-muted-foreground">
                  خودروها: {road.vehicleCount}
                </p>
              </div>
            </Popup>
          </CircleMarker>
        ))
      )}
    </>
  );
}
