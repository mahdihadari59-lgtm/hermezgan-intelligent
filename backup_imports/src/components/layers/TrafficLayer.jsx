// src/map/TrafficLayer.jsx
// FIX #7: hardcoded TRAFFIC_DATA replaced with mapApi + live WebSocket
// updates (FIX #16 — traffic now updates in place as messages arrive
// instead of only loading once on mount).

import React, { useEffect, useRef, useState, useCallback } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';
import { mapApi } from '../services/mapApi';
import { buildPopup } from './utils/popupContent';
import { useLiveChannel } from '../services/useLiveChannel';

const FALLBACK = [
  { id: 't1', lat: 27.2158, lng: 56.2808, level: 'heavy', name: 'چهارراه غزی', delay: 15, speed: 8 },
];

const LEVEL_TEXT = { heavy: '🔴 سنگین', medium: '🟡 نیمه سنگین', light: '🟢 روان' };
const LEVEL_COLOR = { heavy: '#ff4757', medium: '#ffa502', light: '#2ed573' };
const LEVEL_SIZE = { heavy: 24, medium: 18, light: 12 };

const TrafficLayer = () => {
  const map = useMap();
  const layerRef = useRef(null);
  const [trafficData, setTrafficData] = useState([]);

  useEffect(() => {
    let cancelled = false;
    mapApi.getTrafficData(map.getBounds()).then((data) => {
      if (!cancelled) setTrafficData(data && data.length ? data : FALLBACK);
    });
    return () => {
      cancelled = true;
    };
  }, [map]);

  // FIX #16: live traffic updates over WebSocket, merged into state by id.
  useLiveChannel('traffic', (update) => {
    setTrafficData((prev) => {
      const next = new Map(prev.map((t) => [t.id, t]));
      next.set(update.id, { ...next.get(update.id), ...update });
      return Array.from(next.values());
    });
  });

  const render = useCallback(
    (data) => {
      if (!map) return;
      if (layerRef.current) {
        map.removeLayer(layerRef.current);
        layerRef.current = null;
      }
      const group = L.layerGroup();

      data.forEach((item) => {
        const color = LEVEL_COLOR[item.level];
        const size = LEVEL_SIZE[item.level];

        const marker = L.circleMarker([item.lat, item.lng], {
          radius: size, fillColor: color, color: 'white', weight: 3, opacity: 1, fillOpacity: 0.9,
        });

        if (item.level === 'heavy') {
          group.addLayer(
            L.circleMarker([item.lat, item.lng], {
              radius: size * 2.5, fillColor: color, color, weight: 1, opacity: 0.3, fillOpacity: 0.1,
              className: 'traffic-pulse',
            })
          );
        }

        marker.bindPopup(
          buildPopup({
            title: item.name,
            rows: [
              { label: '🚗 سرعت', value: `${item.speed} km/h` },
              { label: '⏱️ تأخیر', value: `${item.delay} دقیقه` },
              { label: '📊 وضعیت', value: LEVEL_TEXT[item.level] },
            ],
            footer: new Date().toLocaleTimeString('fa-IR'),
          })
        );

        group.addLayer(marker);
      });

      group.addTo(map);
      layerRef.current = group;
    },
    [map]
  );

  useEffect(() => {
    if (trafficData.length) render(trafficData);
  }, [trafficData, render]);

  useEffect(
    () => () => {
      if (layerRef.current) {
        map.removeLayer(layerRef.current);
        layerRef.current = null;
      }
    },
    [map]
  );

  return null;
};

export default TrafficLayer;
