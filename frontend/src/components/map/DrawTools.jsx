// src/map/DrawTools.jsx
//
// FIX #13: L.Control.Draw was configured with `edit.featureGroup` set to a
// brand-new L.FeatureGroup() that was never added to the map, and created
// shapes were never added to it either. Leaflet.draw's Edit toolbar edits
// the layers inside that featureGroup — since it was empty and detached,
// Edit had nothing to operate on. Now the featureGroup is added to the map
// and every created shape is pushed into it.
//
// FIX #11: map.on(L.Draw.Event...) listeners are now removed on unmount.

import React, { useEffect, useRef } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet-draw';
import 'leaflet-draw/dist/leaflet.draw.css';

const DrawTools = ({ onCreated, onEdited, onDeleted }) => {
  const map = useMap();
  const drawControlRef = useRef(null);
  const editableLayersRef = useRef(null);

  useEffect(() => {
    if (!map) return undefined;

    const editableLayers = new L.FeatureGroup();
    editableLayers.addTo(map); // <-- was missing; Edit toolbar needs this on the map
    editableLayersRef.current = editableLayers;

    const drawControl = new L.Control.Draw({
      position: 'topleft',
      draw: {
        polyline: { shapeOptions: { color: '#667eea', weight: 3 } },
        polygon: { shapeOptions: { color: '#ff4757', weight: 3 } },
        circle: { shapeOptions: { color: '#2ed573', weight: 3 } },
        rectangle: { shapeOptions: { color: '#ffa502', weight: 3 } },
        marker: true,
      },
      edit: { featureGroup: editableLayers },
    });

    map.addControl(drawControl);
    drawControlRef.current = drawControl;

    const handleCreated = (event) => {
      editableLayers.addLayer(event.layer); // register so Edit/Delete can find it
      onCreated?.(event);
    };
    const handleEdited = (event) => onEdited?.(event);
    const handleDeleted = (event) => onDeleted?.(event);

    map.on(L.Draw.Event.CREATED, handleCreated);
    map.on(L.Draw.Event.EDITED, handleEdited);
    map.on(L.Draw.Event.DELETED, handleDeleted);

    return () => {
      map.off(L.Draw.Event.CREATED, handleCreated);
      map.off(L.Draw.Event.EDITED, handleEdited);
      map.off(L.Draw.Event.DELETED, handleDeleted);
      if (drawControlRef.current) {
        map.removeControl(drawControlRef.current);
        drawControlRef.current = null;
      }
      if (editableLayersRef.current) {
        map.removeLayer(editableLayersRef.current);
        editableLayersRef.current = null;
      }
    };
  }, [map, onCreated, onEdited, onDeleted]);

  return null;
};

export default DrawTools;
