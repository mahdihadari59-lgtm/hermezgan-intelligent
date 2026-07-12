// src/map/RoutingManager.jsx
//
// FIX #2: the public router.project-osrm.org demo server is rate-limited,
// has no SLA, and is explicitly documented by OSRM as "not for production
// use." Routing now reads its base URL from an env var so HDP can point at
// a self-hosted OSRM / GraphHopper / Valhalla instance.
//
// FIX #11: routingControl attaches its own internal map listeners; we now
// remove the control (which detaches them) on unmount, and we also stop
// reacting to prop changes that were previously hardcoded.

import React, { useEffect, useRef } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet-routing-machine';

const ROUTER_BASE_URL =
  process.env.REACT_APP_ROUTING_URL || 'https://osrm.hormozgandriver.ir/route/v1';
// ^ Replace with HDP's own OSRM/GraphHopper/Valhalla deployment before
//   shipping. Falling back to a placeholder subdomain rather than the
//   public demo server keeps this from silently hitting a third party.

const RoutingManager = ({ waypoints, profile = 'driving' }) => {
  const map = useMap();
  const routingRef = useRef(null);

  useEffect(() => {
    if (!map) return undefined;
    if (!waypoints || waypoints.length < 2) return undefined;

    const routingControl = L.Routing.control({
      waypoints: waypoints.map((wp) => L.latLng(wp.lat, wp.lng)),
      routeWhileDragging: true,
      showAlternatives: true,
      fitSelectedRoutes: true,
      lineOptions: { styles: [{ color: '#667eea', weight: 4 }] },
      router: L.Routing.osrmv1({
        serviceUrl: ROUTER_BASE_URL,
        profile,
      }),
    });

    routingControl.addTo(map);
    routingRef.current = routingControl;

    return () => {
      if (routingRef.current) {
        map.removeControl(routingRef.current);
        routingRef.current = null;
      }
    };
  }, [map, waypoints, profile]);

  return null;
};

export default RoutingManager;
