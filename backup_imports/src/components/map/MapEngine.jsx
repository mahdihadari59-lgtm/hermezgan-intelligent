// src/map/MapEngine.jsx
//
// FIX #9: MapLayers.jsx built a second L.control.layers(...) with its own
// copy of the base layers, stacking a duplicate control on top of the
// <LayersControl> already declared here. MapLayers is removed entirely —
// this component is the single source of truth for layer control.
//
// FIX #11: `mapInstance.on('moveend'/'zoomend'/'click', ...)` was never
// paired with `.off(...)`, so remounting MapEngine leaked listeners onto
// whatever Leaflet map instance survived. Handlers are now named refs and
// removed on cleanup.
//
// FIX #12: `useCallback(debounce(...), [map, dispatch])` recreated the
// debounce timer identity on every dependency change, and the timer was
// never cancelled on unmount (a common source of "setState after unmount"
// warnings). Replaced with useMemo + explicit .cancel() on cleanup.

import React, { useEffect, useRef, useState, useCallback, useMemo } from 'react';
import { MapContainer, TileLayer, ZoomControl, ScaleControl, LayersControl } from 'react-leaflet';
import 'leaflet.heat';
import 'leaflet.markercluster';
import 'leaflet-routing-machine';
import 'leaflet-velocity';
import 'leaflet-draw';
import { debounce } from 'lodash';
import { useDispatch, useSelector } from 'react-redux';

import MarkerManager from './MarkerManager';
import ClusterManager from './ClusterManager';
import RoutingManager from './RoutingManager';
import OfflineManager from './OfflineManager';
import OfflineTileLayer from './OfflineTileLayer';
import GeoTiffLayer from './GeoTiffLayer';
import VectorTileLayer from './VectorTileLayer';
import DrawTools from './DrawTools';
import WeatherLayer from './WeatherLayer';
import CameraLayer from './CameraLayer';
import TrafficLayer from './TrafficLayer';
import HospitalLayer from './HospitalLayer';
import FuelLayer from './FuelLayer';
import TourismLayer from './TourismLayer';
import HeatmapLayer from './HeatmapLayer';

import { offlineCache } from '../services/offlineCache';
import { geoService } from '../services/geoService';

import { setMapCenter, setZoom, setMapReady, setLoading, setError } from '../store/slices/mapSlice';

import '../assets/styles/map.css';

const { BaseLayer, Overlay } = LayersControl;

const MapEngine = ({
  initialCenter = [27.2158, 56.2808],
  initialZoom = 13,
  onMapReady,
  onError,
  className = '',
}) => {
  const dispatch = useDispatch();
  const mapRef = useRef(null);
  const [map, setMap] = useState(null);
  const [mapMode, setMapMode] = useState('default');
  const [isOffline, setIsOffline] = useState(false);
  const { markers } = useSelector((state) => state.map);

  const mapConfig = useMemo(
    () => ({
      center: initialCenter,
      zoom: initialZoom,
      maxZoom: 19,
      minZoom: 8,
      zoomControl: false,
      attributionControl: true,
      fadeAnimation: true,
      zoomAnimation: true,
      markerZoomAnimation: true,
      wheelDebounceTime: 40,
      wheelPxPerZoomLevel: 60,
    }),
    [initialCenter, initialZoom]
  );

  // FIX #12: stable debounced handler, cancelled on unmount.
  const debouncedMove = useMemo(
    () =>
      debounce((mapInstance) => {
        const center = mapInstance.getCenter();
        dispatch(setMapCenter({ lat: center.lat, lng: center.lng }));
        dispatch(setZoom(mapInstance.getZoom()));
      }, 300),
    [dispatch]
  );
  useEffect(() => () => debouncedMove.cancel(), [debouncedMove]);

  // FIX #11: named handlers stored so they can be removed on cleanup.
  useEffect(() => {
    if (!map) return undefined;

    const handleMoveEnd = () => debouncedMove(map);
    const handleZoomEnd = () => setMapMode((prev) => (map.getZoom() < 12 ? 'cluster' : prev === 'cluster' ? 'default' : prev));
    const handleClick = (e) => {
      // eslint-disable-next-line no-console
      console.log('Map clicked:', e.latlng);
    };

    map.on('moveend', handleMoveEnd);
    map.on('zoomend', handleZoomEnd);
    map.on('click', handleClick);

    return () => {
      map.off('moveend', handleMoveEnd);
      map.off('zoomend', handleZoomEnd);
      map.off('click', handleClick);
    };
  }, [map, debouncedMove]);

  const handleMapReady = useCallback(() => {
    if (!mapRef.current) return;
    setMap(mapRef.current);
    dispatch(setMapReady(true));
    onMapReady?.(mapRef.current);
  }, [onMapReady, dispatch]);

  const getUserLocation = useCallback(async () => {
    try {
      dispatch(setLoading(true));
      const position = await geoService.getCurrentPosition();
      map?.flyTo([position.lat, position.lng], 15, { duration: 1.5, easeLinearity: 0.25 });
    } catch (error) {
      dispatch(setError(error.message || String(error)));
      onError?.(error);
    } finally {
      dispatch(setLoading(false));
    }
  }, [map, dispatch, onError]);

  const toggleOffline = useCallback(async () => {
    const next = !isOffline;
    setIsOffline(next);
    if (next) await offlineCache.enable();
    else await offlineCache.disable();
  }, [isOffline]);

  const downloadCurrentView = useCallback(
    async (onProgress) => {
      if (!map) return;
      await offlineCache.downloadArea(map.getBounds(), map.getZoom(), onProgress);
    },
    [map]
  );

  return (
    <div className={`map-engine ${className}`}>
      <MapContainer {...mapConfig} ref={mapRef} whenReady={handleMapReady} className="map-engine-container">
        <LayersControl position="topright">
          <BaseLayer checked name="نقشه استاندارد">
            {isOffline ? (
              <OfflineTileLayer />
            ) : (
              <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                maxZoom={19}
              />
            )}
          </BaseLayer>

          <BaseLayer name="نقشه روشن">
            <TileLayer
              url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png"
              attribution='&copy; OpenStreetMap, &copy; CARTO'
              maxZoom={19}
            />
          </BaseLayer>

          <BaseLayer name="تصاویر ماهواره‌ای">
            <TileLayer
              url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
              attribution='&copy; Esri'
              maxZoom={19}
            />
          </BaseLayer>

          <Overlay checked name="🚦 ترافیک"><TrafficLayer /></Overlay>
          <Overlay checked name="📹 دوربین‌ها"><CameraLayer /></Overlay>
          <Overlay checked name="🏥 بیمارستان‌ها"><HospitalLayer /></Overlay>
          <Overlay checked name="⛽ جایگاه‌های سوخت"><FuelLayer /></Overlay>
          <Overlay checked name="🏖️ گردشگری"><TourismLayer /></Overlay>
          <Overlay name="🌤️ آب و هوا"><WeatherLayer /></Overlay>
          <Overlay name="🗺️ لایه‌های جغرافیایی"><GeoTiffLayer datasetUrl={process.env.REACT_APP_DEM_URL} /></Overlay>
          <Overlay name="📐 تایل‌های برداری"><VectorTileLayer /></Overlay>
        </LayersControl>

        {mapMode === 'cluster' ? <ClusterManager /> : <MarkerManager />}
        {mapMode === 'heatmap' && <HeatmapLayer points={markers} />}

        <RoutingManager />
        <DrawTools />

        <ZoomControl position="bottomright" />
        <ScaleControl position="bottomleft" />

        <OfflineManager isOffline={isOffline} onToggle={toggleOffline} onDownload={downloadCurrentView} />
      </MapContainer>

      <div className="map-floating-controls">
        <div className="map-mode-selector">
          {['default', 'heatmap', 'cluster', 'live'].map((mode) => (
            <button
              key={mode}
              className={`mode-btn ${mapMode === mode ? 'active' : ''}`}
              onClick={() => setMapMode(mode)}
              title={mode}
            >
              {{ default: '🗺️', heatmap: '🔥', cluster: '📊', live: '📡' }[mode]}
            </button>
          ))}
        </div>

        <button className="location-btn" onClick={getUserLocation} title="موقعیت من">
          📍
        </button>

        {isOffline && (
          <div className="offline-status">
            <span>📡 آفلاین</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default MapEngine;
