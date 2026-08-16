// src/map/GeoTiffLayer.jsx
//
// FIX #4: the original code fetched a non-existent example.com/sample.tif
// and then overlaid a hardcoded, unrelated PNG at fixed bounds — the raster
// it read was never actually drawn. This version:
//   - takes a `datasetUrl` + `bounds` (or reads bounds from the GeoTIFF's
//     own georeferencing via image.getBoundingBox()) so it works for real
//     HDP layers (DEM / DSM / flood / landuse / population).
//   - rasterizes the actual pixel data onto a canvas and uses that canvas
//     as the image overlay source, so what's fetched is what's shown.
//   - reports load errors instead of failing silently.

import React, { useEffect, useRef, useState } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';
import { fromUrl } from 'geotiff';

// Simple single-band grayscale/heat ramp; swap per dataset type if needed.
function valueToColor(value, min, max) {
  if (Number.isNaN(value)) return [0, 0, 0, 0];
  const t = Math.max(0, Math.min(1, (value - min) / (max - min || 1)));
  const r = Math.round(255 * t);
  const b = Math.round(255 * (1 - t));
  return [r, 60, b, 180];
}

const GeoTiffLayer = ({ datasetUrl, opacity = 0.6 }) => {
  const map = useMap();
  const layerRef = useRef(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!map || !datasetUrl) return undefined;
    let cancelled = false;

    const load = async () => {
      try {
        const tiff = await fromUrl(datasetUrl);
        const image = await tiff.getImage();
        const rasters = await image.readRasters();
        const band = rasters[0];
        const width = image.getWidth();
        const height = image.getHeight();
        const bbox = image.getBoundingBox(); // [west, south, east, north] in the source CRS

        let min = Infinity;
        let max = -Infinity;
        for (let i = 0; i < band.length; i += 1) {
          const v = band[i];
          if (v < min) min = v;
          if (v > max) max = v;
        }

        const canvas = document.createElement('canvas');
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext('2d');
        const imgData = ctx.createImageData(width, height);
        for (let i = 0; i < band.length; i += 1) {
          const [r, g, b, a] = valueToColor(band[i], min, max);
          imgData.data[i * 4] = r;
          imgData.data[i * 4 + 1] = g;
          imgData.data[i * 4 + 2] = b;
          imgData.data[i * 4 + 3] = a;
        }
        ctx.putImageData(imgData, 0, 0);

        if (cancelled) return;

        const bounds = [
          [bbox[1], bbox[0]],
          [bbox[3], bbox[2]],
        ];

        if (layerRef.current) {
          map.removeLayer(layerRef.current);
        }

        const overlay = L.imageOverlay(canvas.toDataURL(), bounds, { opacity });
        overlay.addTo(map);
        layerRef.current = overlay;
        setError(null);
      } catch (err) {
        console.error('[GeoTiffLayer] failed to load', datasetUrl, err);
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
  }, [map, datasetUrl, opacity]);

  if (error) {
    console.warn('[GeoTiffLayer] not rendering due to error:', error);
  }

  return null;
};

export default GeoTiffLayer;
