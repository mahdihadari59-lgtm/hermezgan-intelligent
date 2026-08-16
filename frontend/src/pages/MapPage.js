// src/pages/MapPage.js
import React, { useEffect, useState } from 'react';
import {
  useDispatch,
  useSelector
} from 'react-redux';

import {
  setHotspots,
  selectHotspot,
  clearHotspotSelection,
  toggleHotspots,
  setHotspotFilter
} from '../store';

import {
  setCameras,
  selectCamera,
  clearCameraSelection,
  setCameraFilter,
  setRegionFilter
} from '../store';

import './MapPage.css';

import { MapContainer, TileLayer, useMap } from 'react-leaflet';
import { addNotification, addToast, clearError, setError, setLoading } from '../features/ui/uiSlice';
import mapService from '../services/mapService';
import { selectMarker, setGeolocating, setMapCenter, setMapMode, setMarkers, setSearchQuery, setServiceTypeFilter, setUserLocation, setZoom } from '../features/map/mapSlice';
import hotspotService from '../services/hotspotService';
import cameraService from '../services/cameraService';
import { CameraFilter, CameraInfo, CameraList, CameraMarkers, HotspotFilter, HotspotInfo, HotspotList, HotspotMarkers, MapMarkers, MapPopup, MapSearch } from '../components/Map';

// Map Updater
const MapUpdater = ({ center, zoom }) => {
  const map = useMap();
  useEffect(() => {
    if (map) {
      map.setView([center.lat, center.lng], zoom, { animate: true });
    }
  }, [center, zoom, map]);
  return null;
};

const MapPage = () => {
  const dispatch = useDispatch();

  // State
  const [activeTab, setActiveTab] = useState('services');
  const [] = useState(false);

  // Map State
  const mapState = useSelector(state => state.map);
  const { 
    center, 
    zoom, 
    markers: services, 
    selectedMarker, 
    searchQuery, 
    selectedServiceType, 
    serviceTypes, 
    isGeolocating,
    isLoading,
    error,
    mapMode,
  } = mapState;

  // Hotspot State
  const hotspotState = useSelector(state => state.hotspot);
  const { hotspots, selectedHotspot, showHotspots, hotspotFilter, hotspotTypes } = hotspotState;

  // Camera State
  const cameraState = useSelector(state => state.camera);
  const { cameras, selectedCamera, cameraFilter, regionFilter, regions, statuses } = cameraState;

  // UI State
  const { theme } = useSelector(state => state.ui);

  // Initialize data
  useEffect(() => {
    try {
      dispatch(setLoading(true));

      // Load services
      const mockServices = mapService.getMockServices();
      dispatch(setMarkers(mockServices));

      // Load hotspots
      const mockHotspots = hotspotService.getMockHotspots();
      dispatch(setHotspots(mockHotspots));

      // Load cameras
      const mockCameras = cameraService.getMockCameras();
      dispatch(setCameras(mockCameras));

      // Notification
      dispatch(addNotification({
        title: 'نقشه بارگذاری شد',
        message: 'تمام داده‌ها با موفقیت بارگذاری شدند',
        type: 'success',
      }));

    } catch (error) {
      dispatch(setError(error.message));
      dispatch(addToast({
        message: 'خطا در بارگذاری نقشه',
        type: 'error',
      }));
    } finally {
      dispatch(setLoading(false));
    }
  }, [dispatch]);

  // Get user location
  const handleGetLocation = async () => {
    dispatch(setGeolocating(true));
    try {
      const location = await mapService.getUserLocation();
      dispatch(setUserLocation(location));
      dispatch(setMapCenter({ lat: location.lat, lng: location.lng }));
      dispatch(setZoom(15));

      dispatch(addToast({
        message: 'موقعیت شما دریافت شد',
        type: 'success',
        duration: 2000,
      }));

    } catch (error) {
      dispatch(setError(error.toString()));
      dispatch(setMapCenter({ lat: 27.2158, lng: 56.2808 }));
      
      dispatch(addToast({
        message: 'خطا در دریافت موقعیت',
        type: 'error',
        duration: 3000,
      }));

    } finally {
      dispatch(setGeolocating(false));
      setTimeout(() => dispatch(clearError()), 5000);
    }
  };

  // Filter data
  const filteredServices = services.filter(service => {
    const matchesType = !selectedServiceType || service.type === selectedServiceType;
    const matchesSearch = !searchQuery || 
      service.name.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesType && matchesSearch;
  });

  const filteredHotspots = hotspotFilter === 'all'
    ? hotspots
    : hotspots.filter(h => h.type === hotspotFilter);

  const filteredCameras = cameras.filter(camera => {
    const matchesFilter = cameraFilter === 'all' || camera.status === cameraFilter;
    const matchesRegion = !regionFilter || camera.region === regionFilter;
    return matchesFilter && matchesRegion;
  });

  // Change map mode
  const handleMapModeChange = (mode) => {
    dispatch(setMapMode(mode));
    dispatch(addToast({
      message: `حالت نقشه: ${mode === 'default' ? 'عادی' : mode === 'heatmap' ? 'حرارتی' : mode === 'cluster' ? 'خوشه‌بندی' : 'زنده'}`,
      type: 'info',
      duration: 1500,
    }));
  };

  return (
    <div className={`map-page-full ${theme === 'dark' ? 'dark' : ''}`}>
      {/* Top Panel */}
      <div className="map-top-bar">
        <div className="bar-left">
          <h1>🗺️ نقشه خدمات و سرویس‌ها</h1>
          <span className="mode-badge">{mapMode === 'default' ? 'عادی' : mapMode === 'heatmap' ? '🔥 حرارتی' : mapMode === 'cluster' ? '📊 خوشه‌بندی' : '📡 زنده'}</span>
        </div>
        <div className="bar-right">
          <button
            className={`tab-btn ${activeTab === 'services' ? 'active' : ''}`}
            onClick={() => setActiveTab('services')}
          >
            🏪 خدمات
          </button>
          <button
            className={`tab-btn ${activeTab === 'hotspots' ? 'active' : ''}`}
            onClick={() => setActiveTab('hotspots')}
          >
            🚨 حادثه‌خیز
          </button>
          <button
            className={`tab-btn ${activeTab === 'cameras' ? 'active' : ''}`}
            onClick={() => setActiveTab('cameras')}
          >
            📹 دوربین‌ها
          </button>

          {/* Map Mode Controls */}
          <div className="map-mode-controls">
            <button
              className={`mode-btn ${mapMode === 'default' ? 'active' : ''}`}
              onClick={() => handleMapModeChange('default')}
              title="حالت عادی"
            >
              🗺️
            </button>
            <button
              className={`mode-btn ${mapMode === 'heatmap' ? 'active' : ''}`}
              onClick={() => handleMapModeChange('heatmap')}
              title="نقشه حرارتی"
            >
              🔥
            </button>
            <button
              className={`mode-btn ${mapMode === 'cluster' ? 'active' : ''}`}
              onClick={() => handleMapModeChange('cluster')}
              title="خوشه‌بندی"
            >
              📊
            </button>
          </div>

          <button
            className="locate-btn"
            onClick={handleGetLocation}
            disabled={isGeolocating}
          >
            {isGeolocating ? '⏳' : '📍'} موقعیت من
          </button>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="error-banner">
          <span>⚠️ {error}</span>
          <button onClick={() => dispatch(clearError())}>✕</button>
        </div>
      )}

      {/* Main Content */}
      <div className="map-content-full">
        {/* Sidebar */}
        <div className="map-sidebar-full">
          {activeTab === 'services' && (
            <div className="sidebar-content">
              <MapSearch
                searchQuery={searchQuery}
                onSearchChange={(q) => dispatch(setSearchQuery(q))}
                selectedServiceType={selectedServiceType}
                onServiceTypeChange={(type) => dispatch(setServiceTypeFilter(type))}
                serviceTypes={serviceTypes}
              />
              <div className="sidebar-list">
                {filteredServices.map((service) => (
                  <div
                    key={service.id}
                    className={`list-item ${selectedMarker?.id === service.id ? 'selected' : ''}`}
                    onClick={() => dispatch(selectMarker(service))}
                  >
                    <span className="item-icon">📍</span>
                    <div className="item-info">
                      <h4>{service.name}</h4>
                      <p>{service.distance}km • ⭐{service.rating}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'hotspots' && (
            <div className="sidebar-content">
              <HotspotFilter
                hotspotFilter={hotspotFilter}
                onFilterChange={(f) => dispatch(setHotspotFilter(f))}
                hotspotTypes={hotspotTypes}
                showHotspots={showHotspots}
                onToggleHotspots={() => dispatch(toggleHotspots())}
              />
              <HotspotList
                hotspots={filteredHotspots}
                selectedHotspot={selectedHotspot}
                onHotspotSelect={(h) => dispatch(selectHotspot(h))}
                hotspotTypes={hotspotTypes}
              />
            </div>
          )}

          {activeTab === 'cameras' && (
            <div className="sidebar-content">
              <CameraFilter
                cameraFilter={cameraFilter}
                regionFilter={regionFilter}
                onFilterChange={(f) => dispatch(setCameraFilter(f))}
                onRegionChange={(r) => dispatch(setRegionFilter(r))}
                regions={regions}
                statuses={statuses}
              />
              <CameraList
                cameras={filteredCameras}
                selectedCamera={selectedCamera}
                onCameraSelect={(c) => dispatch(selectCamera(c))}
              />
            </div>
          )}
        </div>

        {/* Map */}
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; OpenStreetMap'
          />
          <MapUpdater center={center} zoom={zoom} />

          {/* Services */}
          {activeTab === 'services' && (
            <MapMarkers
              markers={filteredServices}
              selectedMarker={selectedMarker}
              onMarkerClick={(m) => dispatch(selectMarker(m))}
              serviceTypes={serviceTypes}
            />
          )}

          {/* Hotspots */}
          {activeTab === 'hotspots' && showHotspots && (
            <HotspotMarkers
              hotspots={filteredHotspots}
              selectedHotspot={selectedHotspot}
              onHotspotClick={(h) => dispatch(selectHotspot(h))}
              hotspotTypes={hotspotTypes}
            />
          )}

          {/* Cameras */}
          {activeTab === 'cameras' && (
            <CameraMarkers
              cameras={filteredCameras}
              selectedCamera={selectedCamera}
              onCameraClick={(c) => dispatch(selectCamera(c))}
              cameraTypes={cameraState.cameraTypes}
            />
          )}
      </div>

      {/* Detail Panels */}
      {activeTab === 'services' && selectedMarker && (
        <MapPopup
          service={selectedMarker}
          onClose={() => dispatch(selectMarker(null))}
          onGetDirections={() => {
            dispatch(addToast({
              message: `مسیریابی به ${selectedMarker.name}`,
              type: 'info',
              duration: 2000,
            }));
          }}
        />
      )}

      {activeTab === 'hotspots' && selectedHotspot && (
        <HotspotInfo
          hotspot={selectedHotspot}
          hotspotTypes={hotspotTypes}
          onClose={() => dispatch(clearHotspotSelection())}
          onReport={() => {
            dispatch(addToast({
              message: 'گزارش حادثه ثبت شد',
              type: 'success',
              duration: 2000,
            }));
          }}
        />
      )}

      {activeTab === 'cameras' && selectedCamera && (
        <CameraInfo
          camera={selectedCamera}
          onClose={() => dispatch(clearCameraSelection())}
          onReportIssue={(id, msg) => {
            dispatch(addToast({
              message: `گزارش مشکل برای ${selectedCamera.name} ثبت شد`,
              type: 'success',
              duration: 2000,
            }));
            console.log('Report:', id, msg);
          }}
        />
      )}

      {/* Loading Overlay */}
      {isLoading && (
        <div className="loading-overlay">
          <div className="loading-spinner"></div>
          <p>در حال بارگذاری نقشه...</p>
        </div>
      )}
    </div>
  );
};

export default MapPage;
