// src/map/HeatmapLayer.jsx
//
// FIX #15: leaflet.heat was listed as a dependency but no component ever
// used it. This renders a real heat layer from point data (e.g. traffic
// density, ride requests) and is only mounted when mapMode === 'heatmap'
// in MapEngine.

import { useEffect, useRef } from 'react';
import { useMap } from 'react-leaflet';
import 'leaflet.heat';
import L from 'leaflet';

/**
 * @param {Array<{lat:number,lng:number,intensity?:number}>} points
 */
const HeatmapLayer = ({ points = [], radius = 25, blur = 15, max = 1.0 }) => {
  const map = useMap();
  const layerRef = useRef(null);

  useEffect(() => {
    if (!map) return undefined;

    const heatPoints = points.map((p) => [p.lat, p.lng, p.intensity ?? 0.5]);
    const heatLayer = L.heatLayer(heatPoints, { radius, blur, max });
    heatLayer.addTo(map);
    layerRef.current = heatLayer;

    return () => {
      if (layerRef.current) {
        map.removeLayer(layerRef.current);
        layerRef.current = null;
      }
    };
  }, [map, points, radius, blur, max]);

  return null;
};

export default HeatmapLayer;
