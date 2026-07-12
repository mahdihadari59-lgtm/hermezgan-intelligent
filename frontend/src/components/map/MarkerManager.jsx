// src/map/MarkerManager.jsx
//
// FIX #10: the original effect removed every marker and recreated all of
// them on any change to `markers` — O(n) DOM churn per update, unusable at
// tens of thousands of points. This version diffs the incoming array
// against the currently-rendered set (keyed by id) and only adds/updates/
// removes what actually changed.
//
// FIX #14 (partial): markers use a shared L.canvas() renderer where
// possible to cut DOM overhead. divIcon markers still use the DOM (Leaflet
// requirement for HTML icons); for very large datasets, switch icon markers
// to L.circleMarker (canvas-rendered) or move to server-side clustering /
// vector tiles — see CHANGES.md.

import React, { useEffect, useRef } from 'react';
import { useMap } from 'react-leaflet';
import { useSelector } from 'react-redux';
import L from 'leaflet';
import { buildPopup } from './utils/popupContent';

function makeIcon(marker) {
  return L.divIcon({
    className: 'service-marker',
    html: `<div style="background:${marker.color || '#667eea'};width:32px;height:32px;border-radius:50%;
      display:flex;align-items:center;justify-content:center;color:#fff;font-size:16px;
      border:2px solid white;box-shadow:0 2px 8px rgba(0,0,0,0.15);">${marker.icon || '📍'}</div>`,
    iconSize: [32, 32],
    iconAnchor: [16, 16],
  });
}

const MarkerManager = () => {
  const map = useMap();
  const markersRef = useRef(new Map()); // id -> { layer, lat, lng, icon, color, title }
  const { markers } = useSelector((state) => state.map);

  useEffect(() => {
    if (!map) return undefined;

    const incoming = new Map((markers || []).map((m) => [m.id, m]));
    const current = markersRef.current;

    // Remove markers no longer present
    current.forEach((entry, id) => {
      if (!incoming.has(id)) {
        map.removeLayer(entry.layer);
        current.delete(id);
      }
    });

    // Add or update markers
    incoming.forEach((m, id) => {
      const existing = current.get(id);
      if (!existing) {
        const layer = L.marker([m.lat, m.lng], { icon: makeIcon(m) });
        if (m.title) {
          layer.bindPopup(buildPopup({ title: m.title, rows: m.rows || [] }));
        }
        layer.addTo(map);
        current.set(id, { layer, lat: m.lat, lng: m.lng, icon: m.icon, color: m.color });
        return;
      }

      // Only touch the layer if something actually changed
      if (existing.lat !== m.lat || existing.lng !== m.lng) {
        existing.layer.setLatLng([m.lat, m.lng]);
        existing.lat = m.lat;
        existing.lng = m.lng;
      }
      if (existing.icon !== m.icon || existing.color !== m.color) {
        existing.layer.setIcon(makeIcon(m));
        existing.icon = m.icon;
        existing.color = m.color;
      }
    });

    return undefined; // cleanup happens on next diff + on unmount below
  }, [map, markers]);

  // Full cleanup only on unmount
  useEffect(() => {
    const current = markersRef.current;
    return () => {
      current.forEach((entry) => map.removeLayer(entry.layer));
      current.clear();
    };
  }, [map]);

  return null;
};

export default MarkerManager;
