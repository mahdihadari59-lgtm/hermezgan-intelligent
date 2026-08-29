// src/map/FuelLayer.jsx
// FIX #7: data now comes from mapApi instead of being hardcoded.

import React, { useEffect, useRef, useCallback, useState } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';
import { mapApi } from '../services/mapApi';
import { buildPopup } from './utils/popupContent';

const FALLBACK = [
  { id: 1, name: 'پمپ بنزین آزادی', lat: 27.2158, lng: 56.2808, type: 'gasoline', cng: true, diesel: true, hours: '۲۴ ساعته' },
];

const FuelLayer = () => {
  const map = useMap();
  const layerRef = useRef(null);
  const [stations, setStations] = useState([]);

  useEffect(() => {
    let cancelled = false;
    mapApi.getFuelStations().then((data) => {
      if (!cancelled) setStations(data && data.length ? data : FALLBACK);
    });
    return () => {
      cancelled = true;
    };
  }, []);

  const createIcon = useCallback(
    (s) =>
      L.divIcon({
        className: 'fuel-marker',
        html: `<div style="background:${s.cng ? '#ffa502' : '#2ed573'};width:36px;height:36px;border-radius:50%;
        display:flex;align-items:center;justify-content:center;border:3px solid white;
        box-shadow:0 2px 8px rgba(0,0,0,0.15);font-size:18px;">⛽</div>`,
        iconSize: [36, 36],
        iconAnchor: [18, 18],
      }),
    []
  );

  useEffect(() => {
    if (!map || !stations.length) return undefined;
    if (layerRef.current) map.removeLayer(layerRef.current);

    const group = L.layerGroup();
    stations.forEach((s) => {
      const marker = L.marker([s.lat, s.lng], { icon: createIcon(s) });
      marker.bindPopup(
        buildPopup({
          title: s.name,
          rows: [
            { label: '⛽ بنزین', value: s.type === 'gasoline' ? '✅' : '❌' },
            { label: '🔵 CNG', value: s.cng ? '✅' : '❌' },
            { label: '⛽ گازوئیل', value: s.diesel ? '✅' : '❌' },
            { label: '🕐', value: s.hours },
          ],
        })
      );
      group.addLayer(marker);
    });
    group.addTo(map);
    layerRef.current = group;

    return () => {
      if (layerRef.current) {
        map.removeLayer(layerRef.current);
        layerRef.current = null;
      }
    };
  }, [map, stations, createIcon]);

  return null;
};

export default FuelLayer;
