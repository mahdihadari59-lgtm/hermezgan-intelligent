// src/map/CameraLayer.jsx
//
// FIX #7: camera locations were a hardcoded CAMERA_DATA array baked into
// the bundle. Now loaded from mapApi (backed by HDP's core.db / geo.db per
// the 8-database split), with the old array kept only as an offline/dev
// fallback if the API call fails.
// FIX #8: popup "گزارش" button used onclick="alert(...)" — replaced with a
// real DOM event listener via buildPopup().

import React, { useEffect, useRef, useCallback, useState } from 'react';
import { useMap } from 'react-leaflet';
import { useDispatch } from 'react-redux';
import L from 'leaflet';
import { mapApi } from '../services/mapApi';
import { buildPopup } from './utils/popupContent';
import { selectCamera } from '../store/slices/cameraSlice';

const FALLBACK_CAMERA_DATA = [
  { id: 'ba-001', name: 'چهارراه غزی', lat: 27.2158, lng: 56.2808, status: 'active', types: ['traffic-light', 'speed'] },
  { id: 'ba-002', name: 'میدان سپاه', lat: 27.2200, lng: 56.2850, status: 'active', types: ['traffic-light'] },
];

const STATUS_COLORS = { active: '#2ed573', installing: '#ffa502', pending: '#ff4757' };
const STATUS_TEXT = { active: '✅ فعال', installing: '⚠️ در حال نصب', pending: '🔴 نیاز فوری' };

const CameraLayer = () => {
  const map = useMap();
  const dispatch = useDispatch();
  const layerRef = useRef(null);
  const [cameras, setCameras] = useState([]);

  useEffect(() => {
    let cancelled = false;
    mapApi.getCameras().then((data) => {
      if (cancelled) return;
      setCameras(data && data.length ? data : FALLBACK_CAMERA_DATA);
    });
    return () => {
      cancelled = true;
    };
  }, []);

  const createIcon = useCallback((camera) => {
    const color = STATUS_COLORS[camera.status] || '#667eea';
    const isActive = camera.status === 'active';
    return L.divIcon({
      className: `camera-marker ${camera.status}`,
      html: `<div style="background:${color};width:40px;height:40px;border-radius:50%;display:flex;
        align-items:center;justify-content:center;border:3px solid white;box-shadow:0 2px 8px rgba(0,0,0,0.15);
        font-size:18px;position:relative;">📹
        ${isActive ? '<div style="position:absolute;top:-4px;right:-4px;width:12px;height:12px;background:#2ed573;border-radius:50%;border:2px solid white;"></div>' : ''}
      </div>`,
      iconSize: [40, 40],
      iconAnchor: [20, 20],
    });
  }, []);

  useEffect(() => {
    if (!map || !cameras.length) return undefined;
    if (layerRef.current) {
      map.removeLayer(layerRef.current);
      layerRef.current = null;
    }

    const group = L.layerGroup();
    cameras.forEach((camera) => {
      const marker = L.marker([camera.lat, camera.lng], { icon: createIcon(camera) });

      marker.bindPopup(
        buildPopup({
          title: camera.name,
          rows: [
            { label: '📊 وضعیت', value: STATUS_TEXT[camera.status] },
            ...(camera.types ? [{ label: '🎯 نوع', value: camera.types.join('، ') }] : []),
          ],
          actions: [
            {
              label: '🚨 گزارش',
              tone: 'danger',
              onClick: () => mapApi.reportCameraIssue?.(camera.id),
            },
          ],
        })
      );

      marker.on('click', () => dispatch(selectCamera(camera)));
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
  }, [map, cameras, createIcon, dispatch]);

  return null;
};

export default CameraLayer;
