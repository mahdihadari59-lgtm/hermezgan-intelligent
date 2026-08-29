// src/map/ClusterManager.jsx
//
// FIX #1: react-leaflet-cluster requires real <Marker> (or other Leaflet
// layer) children — it reads `position`/`icon` props off each child and
// hands them to Leaflet.markercluster. The original code rendered bare
// <div lat=... lng=...> elements, which react-leaflet-cluster cannot read;
// nothing would ever render.
//
// FIX #14 (partial): for large marker counts we opt into a canvas renderer
// so DOM node count stays low. Full WebGL/supercluster rendering is a
// backend-assisted follow-up (see CHANGES.md item 14/17).

import React, { useMemo } from 'react';
import { Marker, Popup, useMap } from 'react-leaflet';
import MarkerClusterGroup from 'react-leaflet-cluster';
import { useSelector } from 'react-redux';
import L from 'leaflet';

const CLUSTER_STYLE = {
  small: { size: 40, fontSize: 14, color: '#2ed573' },
  medium: { size: 50, fontSize: 16, color: '#ffa502' },
  large: { size: 60, fontSize: 18, color: '#ff6348' },
  xlarge: { size: 70, fontSize: 20, color: '#ff4757' },
};

function createClusterIcon(cluster) {
  const count = cluster.getChildCount();
  const key = count < 10 ? 'small' : count < 50 ? 'medium' : count < 100 ? 'large' : 'xlarge';
  const { size, fontSize, color } = CLUSTER_STYLE[key];

  return L.divIcon({
    html: `<div style="background:${color};color:#fff;border-radius:50%;width:${size}px;height:${size}px;
      display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:${fontSize}px;
      border:3px solid white;box-shadow:0 2px 12px rgba(0,0,0,0.2);">${count}</div>`,
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
    className: 'cluster-icon',
  });
}

function markerIcon(marker) {
  return L.divIcon({
    className: 'service-marker',
    html: `<div style="background:${marker.color || '#667eea'};width:32px;height:32px;border-radius:50%;
      display:flex;align-items:center;justify-content:center;color:#fff;font-size:16px;
      border:2px solid white;box-shadow:0 2px 8px rgba(0,0,0,0.15);">${marker.icon || '📍'}</div>`,
    iconSize: [32, 32],
    iconAnchor: [16, 16],
  });
}

const ClusterManager = () => {
  const map = useMap();
  const { markers } = useSelector((state) => state.map);

  // Use canvas renderer for the underlying markers to cut down on per-marker
  // DOM overhead (issue #14). This is bound once per map instance.
  const renderer = useMemo(() => L.canvas({ padding: 0.5 }), [map]);

  const items = useMemo(() => markers || [], [markers]);

  return (
    <MarkerClusterGroup
      chunkedLoading
      maxClusterRadius={80}
      spiderfyOnMaxZoom
      showCoverageOnHover
      zoomToBoundsOnClick
      iconCreateFunction={createClusterIcon}
      spiderLegPolylineOptions={{ weight: 1.5, color: '#667eea', opacity: 0.5 }}
      polygonOptions={{ fillColor: '#667eea', fillOpacity: 0.15, color: '#667eea', weight: 2 }}
    >
      {items.map((marker) => (
        <Marker
          key={marker.id}
          position={[marker.lat, marker.lng]}
          icon={markerIcon(marker)}
          renderer={renderer}
        >
          {marker.title && <Popup>{marker.title}</Popup>}
        </Marker>
      ))}
    </MarkerClusterGroup>
  );
};

export default ClusterManager;
