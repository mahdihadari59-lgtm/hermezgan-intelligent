// src/map/TourismLayer.jsx
// FIX #7: data now comes from mapApi instead of being hardcoded.
// Also fixed a latent bug: `background: '#ff6b6b';` inside the template
// literal included the quote marks in the CSS value (`background: '#ff6b6b'`
// is invalid CSS), so every tourism marker silently rendered with no
// background color.

import React, { useEffect, useRef, useCallback, useState } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';
import { mapApi } from '../services/mapApi';
import { buildPopup } from './utils/popupContent';

const FALLBACK = [
  { id: 1, name: 'جزیره هرمز', lat: 27.08, lng: 56.45, type: 'island', description: 'جزیره رنگین‌کمان با خاک سرخ خوراکی' },
];

const TourismLayer = () => {
  const map = useMap();
  const layerRef = useRef(null);
  const [sites, setSites] = useState([]);

  useEffect(() => {
    let cancelled = false;
    mapApi.getTourismSites?.().then((data) => {
      if (!cancelled) setSites(data && data.length ? data : FALLBACK);
    }) ?? setSites(FALLBACK);
    return () => {
      cancelled = true;
    };
  }, []);

  const createIcon = useCallback(
    () =>
      L.divIcon({
        className: 'tourism-marker',
        html: `<div style="background:#ff6b6b;width:36px;height:36px;border-radius:50%;
        display:flex;align-items:center;justify-content:center;border:3px solid white;
        box-shadow:0 2px 8px rgba(0,0,0,0.15);font-size:18px;">🏖️</div>`,
        iconSize: [36, 36],
        iconAnchor: [18, 18],
      }),
    []
  );

  useEffect(() => {
    if (!map || !sites.length) return undefined;
    if (layerRef.current) map.removeLayer(layerRef.current);

    const group = L.layerGroup();
    sites.forEach((site) => {
      const marker = L.marker([site.lat, site.lng], { icon: createIcon() });
      marker.bindPopup(buildPopup({ title: site.name, rows: [{ label: '', value: site.description }] }));
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
  }, [map, sites, createIcon]);

  return null;
};

export default TourismLayer;
