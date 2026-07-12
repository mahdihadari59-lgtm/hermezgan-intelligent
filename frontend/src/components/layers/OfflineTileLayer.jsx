// src/map/OfflineTileLayer.jsx
//
// The original MapEngine pointed the "offline" base layer at
// /offline-tiles/{z}/{x}/{y}.png, a static path that was never populated —
// downloadArea() (now offlineCache.downloadArea, see FIX #5) stores tiles
// as blobs in IndexedDB, not as files on disk. This custom Leaflet
// TileLayer overrides tile creation to read from offlineCache instead, so
// what gets downloaded is actually what gets displayed offline.

import React, { useEffect, useRef } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';
import { offlineCache } from '../services/offlineCache';

const OfflineTileLayerImpl = L.TileLayer.extend({
  createTile(coord, done) {
    const tile = document.createElement('img');
    const key = `${coord.z}/${coord.x}/${coord.y}`;

    offlineCache
      .getTile(key)
      .then((cached) => {
        if (cached?.blob) {
          tile.src = URL.createObjectURL(cached.blob);
          done(null, tile);
        } else {
          done(new Error('Tile not cached offline'), tile);
        }
      })
      .catch((err) => done(err, tile));

    return tile;
  },
});

const OfflineTileLayer = () => {
  const map = useMap();
  const layerRef = useRef(null);

  useEffect(() => {
    if (!map) return undefined;
    const layer = new OfflineTileLayerImpl('', {
      maxZoom: 18,
      attribution: '&copy; OpenStreetMap (آفلاین — از حافظه دستگاه)',
    });
    layer.addTo(map);
    layerRef.current = layer;

    return () => {
      if (layerRef.current) {
        map.removeLayer(layerRef.current);
        layerRef.current = null;
      }
    };
  }, [map]);

  return null;
};

export default OfflineTileLayer;
