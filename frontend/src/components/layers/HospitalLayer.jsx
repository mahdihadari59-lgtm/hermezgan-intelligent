// src/map/HospitalLayer.jsx
// FIX #7: data now comes from mapApi instead of being hardcoded.

import React, { useEffect, useRef, useCallback, useState } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';
import { mapApi } from '../services/mapApi';
import { buildPopup } from './utils/popupContent';

const TYPE_ICON = { general: '🏥', pediatric: '👶', specialized: '💉' };
const TYPE_COLOR = { general: '#ff4757', pediatric: '#2ed573', specialized: '#1e90ff' };

const FALLBACK = [
  { id: 1, name: 'بیمارستان شهید محمدی', lat: 27.2158, lng: 56.2808, type: 'general', beds: 350, emergency: true, phone: '۰۷۶-۳۳۳۳۲۰۰۰', address: 'بلوار امام خمینی' },
];

const HospitalLayer = () => {
  const map = useMap();
  const layerRef = useRef(null);
  const [hospitals, setHospitals] = useState([]);

  useEffect(() => {
    let cancelled = false;
    mapApi.getHospitals().then((data) => {
      if (!cancelled) setHospitals(data && data.length ? data : FALLBACK);
    });
    return () => {
      cancelled = true;
    };
  }, []);

  const createIcon = useCallback(
    (h) =>
      L.divIcon({
        className: 'hospital-marker',
        html: `<div style="background:${TYPE_COLOR[h.type] || '#667eea'};width:40px;height:40px;border-radius:50%;
        display:flex;align-items:center;justify-content:center;border:3px solid white;
        box-shadow:0 2px 8px rgba(0,0,0,0.15);font-size:20px;">${TYPE_ICON[h.type] || '🏥'}</div>`,
        iconSize: [40, 40],
        iconAnchor: [20, 20],
      }),
    []
  );

  useEffect(() => {
    if (!map || !hospitals.length) return undefined;
    if (layerRef.current) map.removeLayer(layerRef.current);

    const group = L.layerGroup();
    hospitals.forEach((h) => {
      const marker = L.marker([h.lat, h.lng], { icon: createIcon(h) });
      marker.bindPopup(
        buildPopup({
          title: h.name,
          rows: [
            { label: '🏥 تخت', value: h.beds },
            { label: '', value: h.emergency ? '🚨 اورژانس ۲۴ ساعته' : '🚫 بدون اورژانس' },
            { label: '📞', value: h.phone },
            { label: '📍', value: h.address },
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
  }, [map, hospitals, createIcon]);

  return null;
};

export default HospitalLayer;
