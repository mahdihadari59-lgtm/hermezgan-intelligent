// src/map/WeatherLayer.jsx
//
// FIX #6: the original layer displayed a hardcoded, uniform wind grid
// (Array(10).fill(Array(10).fill(5))) — it always showed the same fake
// wind everywhere regardless of real conditions. This version fetches real
// gridded wind data (u/v components) from mapApi, which should proxy one
// of ECMWF / NOAA GFS / OpenWeather / Windy depending on what HDP has a
// license/key for. Nothing is rendered until real data arrives.

import React, { useEffect, useRef, useState } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet-velocity';
import { mapApi } from '../services/mapApi';

const WeatherLayer = () => {
  const map = useMap();
  const layerRef = useRef(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!map) return undefined;
    let cancelled = false;

    const load = async () => {
      try {
        const data = await mapApi.getWindData(map.getBounds());
        if (cancelled || !data) return;

        const weatherLayer = L.velocityLayer({
          displayValues: true,
          displayOptions: {
            velocityType: 'Wind',
            position: 'bottomleft',
            emptyString: 'داده‌ای موجود نیست',
            angleConvention: 'bearingCW',
            showCardinal: true,
            speedUnit: 'm/s',
          },
          data,
          colorScale: [
            '#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8',
            '#ffffbf', '#fee090', '#fdae61', '#f46d43', '#d73027',
          ],
        });

        if (layerRef.current) map.removeLayer(layerRef.current);
        weatherLayer.addTo(map);
        layerRef.current = weatherLayer;
        setError(null);
      } catch (err) {
        console.error('[WeatherLayer] failed to load wind data', err);
        if (!cancelled) setError(err.message || String(err));
      }
    };

    load();

    return () => {
      cancelled = true;
      if (layerRef.current) {
        map.removeLayer(layerRef.current);
        layerRef.current = null;
      }
    };
  }, [map]);

  if (error) console.warn('[WeatherLayer] not rendering due to error:', error);

  return null;
};

export default WeatherLayer;
