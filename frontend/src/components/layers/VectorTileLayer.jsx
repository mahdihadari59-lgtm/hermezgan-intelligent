// src/map/VectorTileLayer.jsx
//
// FIX #3: OpenStreetMap does not serve protobuf vector tiles at
// tile.openstreetmap.org/{z}/{x}/{y}.pbf — that endpoint 404s. Vector tiles
// now come from a configurable source (MapTiler / OpenMapTiles /
// TileServer-GL / HDP's own tile service). If no URL is configured, the
// layer renders nothing instead of silently failing against a bad URL.

import React, { useEffect, useRef } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet.vectorgrid';

const VECTOR_TILE_URL = process.env.REACT_APP_VECTOR_TILE_URL; // e.g. HDP tileserver-gl endpoint
const VECTOR_TILE_KEY = process.env.REACT_APP_VECTOR_TILE_KEY; // if using MapTiler etc.

const VectorTileLayer = () => {
  const map = useMap();
  const layerRef = useRef(null);

  useEffect(() => {
    if (!map) return undefined;

    if (!VECTOR_TILE_URL) {
      console.warn(
        '[VectorTileLayer] REACT_APP_VECTOR_TILE_URL is not set — skipping vector tile layer. ' +
          'Point this at MapTiler/OpenMapTiles/TileServer-GL or an HDP-hosted endpoint.'
      );
      return undefined;
    }

    const url = VECTOR_TILE_KEY
      ? `${VECTOR_TILE_URL}?key=${VECTOR_TILE_KEY}`
      : VECTOR_TILE_URL;

    const vectorLayer = L.vectorGrid.protobuf(url, {
      vectorTileLayerStyles: {
        water: { fillColor: '#b3d9ff', fillOpacity: 0.8, weight: 0 },
        landuse: { fillColor: '#e5e5e5', fillOpacity: 0.5, weight: 0 },
        road: { color: '#ff0000', weight: 2, opacity: 0.8 },
      },
      maxZoom: 19,
      minZoom: 10,
      attribution: '&copy; OpenMapTiles &copy; OpenStreetMap contributors',
    });

    vectorLayer.on('tileerror', (err) => {
      console.error('[VectorTileLayer] tile error', err);
    });

    vectorLayer.addTo(map);
    layerRef.current = vectorLayer;

    return () => {
      if (layerRef.current) {
        map.removeLayer(layerRef.current);
        layerRef.current = null;
      }
    };
  }, [map]);

  return null;
};

export default VectorTileLayer;
