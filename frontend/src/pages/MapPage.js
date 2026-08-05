import React, { useEffect, useState, useCallback } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { MapContainer as LeafletMapContainer, TileLayer, useMap, Marker, Popup, Circle, Polyline } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import MapMarkers from '../components/Map/MapMarkers';
import HotspotMarkers from '../components/Map/HotspotMarkers';
import CameraMarkers from '../components/Map/CameraMarkers';
import MapSearch from '../components/Map/MapSearch';
import MapPopup from '../components/Map/MapPopup';
import HotspotFilter from '../components/Hotspots/HotspotFilter';
import HotspotList from '../components/Hotspots/HotspotList';
import CameraFilter from '../components/Map/CameraFilter';
import CameraList from '../components/Map/CameraList';
import CameraInfo from '../components/Map/CameraInfo';
import HotspotInfo from '../components/Map/HotspotInfo';
import mapService from '../services/mapService';
import hotspotService from '../services/hotspotService';
import cameraService from '../services/cameraService';
import {
  setMapCenter, setZoom, setMarkers, selectMarker, setSearchQuery,
  setServiceTypeFilter, setUserLocation, setGeolocating,
  setLoading as setMapLoading, setError as setMapError, clearError as clearMapError,
} from '../store/slices/mapSlice';
import {
  setHotspots, selectHotspot, clearHotspotSelection,
  toggleHotspots, setHotspotFilter,
} from '../store/slices/hotspotSlice';
import {
  setCameras, selectCamera, clearCameraSelection,
  setCameraFilter, setRegionFilter,
} from '../store/slices/cameraSlice';
import './MapPage.css';

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const MapUpdater = ({ center, zoom }) => {
  const map = useMap();
  useEffect(() => {
    if (map) map.setView([center.lat, center.lng], zoom, { animate: true });
  }, [center, zoom, map]);
  return null;
};

const MapBounds = ({ markers }) => {
  const map = useMap();
  useEffect(() => {
    if (markers.length > 0) {
      const bounds = L.latLngBounds(markers.map(m => [m.lat, m.lng]));
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [markers, map]);
  return null;
};

const MapPage = () => {
  const dispatch = useDispatch();
  const mapState = useSelector(state => state.map);
  const { center, zoom, markers: services, selectedMarker, searchQuery, selectedServiceType, serviceTypes, userLocation, isGeolocating, isLoading: mapLoading, error: mapError } = mapState;
  const hotspotState = useSelector(state => state.hotspot);
  const { hotspots, selectedHotspot, showHotspots, hotspotFilter, hotspotTypes } = hotspotState;
  const cameraState = useSelector(state => state.camera);
  const { cameras, selectedCamera, cameraFilter, regionFilter, regions, statuses, cameraTypes } = cameraState;
  const [activeTab, setActiveTab] = useState('services');
  const [showSidebar, setShowSidebar] = useState(true);
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);
  const [routeInfo, setRouteInfo] = useState(null);
  const [isRouteActive, setIsRouteActive] = useState(false);
  const [routeStart, setRouteStart] = useState(null);
  const [routeEnd, setRouteEnd] = useState(null);
  const [mapLoaded, setMapLoaded] = useState(false);

  useEffect(() => {
    const handleResize = () => {
      const mobile = window.innerWidth < 768;
      setIsMobile(mobile);
      if (mobile) setShowSidebar(false);
      else setShowSidebar(true);
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  useEffect(() => {
    const loadData = async () => {
      try {
        dispatch(setMapLoading(true));
        dispatch(setMarkers(mapService.getMockServices()));
        dispatch(setHotspots(hotspotService.getMockHotspots()));
        dispatch(setCameras(cameraService.getMockCameras()));
        dispatch(setMapCenter({ lat: 27.2158, lng: 56.2808 }));
        setMapLoaded(true);
      } catch (error) {
        dispatch(setMapError(error.message));
      } finally {
        dispatch(setMapLoading(false));
      }
    };
    loadData();
  }, [dispatch]);

  useEffect(() => {
    if (navigator.geolocation) handleGetLocation();
  }, []);

  const handleGetLocation = useCallback(async () => {
    dispatch(setGeolocating(true));
    try {
      const location = await mapService.getUserLocation();
      dispatch(setUserLocation(location));
      dispatch(setMapCenter({ lat: location.lat, lng: location.lng }));
      dispatch(setZoom(15));
    } catch (error) {
      dispatch(setMapError('موقعیت شما پیدا نشد. موقعیت پیش‌فرض بندرعباس تنظیم شد.'));
      dispatch(setMapCenter({ lat: 27.2158, lng: 56.2808 }));
      dispatch(setZoom(13));
    } finally {
      dispatch(setGeolocating(false));
    }
  }, [dispatch]);

  const handleSearch = useCallback(async () => {
    if (!searchQuery.trim()) return;
    dispatch(setMapLoading(true));
    try {
      const results = await mapService.searchLocations(searchQuery, userLocation?.lat, userLocation?.lng);
      if (results.results?.length > 0) {
        dispatch(setMarkers(results.results));
        const first = results.results[0];
        dispatch(setMapCenter({ lat: first.lat, lng: first.lng }));
        dispatch(setZoom(14));
      } else {
        dispatch(setMapError('نتیجه‌ای یافت نشد'));
      }
    } catch (error) {
      dispatch(setMapError('خطا در جستجو'));
    } finally {
      dispatch(setMapLoading(false));
    }
  }, [searchQuery, userLocation, dispatch]);

  const handleGetDirections = useCallback(async (service) => {
    if (!userLocation) {
      dispatch(setMapError('لطفاً ابتدا موقعیت خود را بدست آورید'));
      return;
    }
    try {
      dispatch(setMapLoading(true));
      const route = await mapService.getRoute(userLocation.lat, userLocation.lng, service.lat, service.lng);
      setRouteInfo(route);
      setIsRouteActive(true);
      setRouteStart(userLocation);
      setRouteEnd(service);
      dispatch(setZoom(14));
    } catch (error) {
      dispatch(setMapError('خطا در دریافت مسیریابی'));
    } finally {
      dispatch(setMapLoading(false));
    }
  }, [userLocation, dispatch]);

  const clearRoute = useCallback(() => {
    setIsRouteActive(false);
    setRouteInfo(null);
    setRouteStart(null);
    setRouteEnd(null);
  }, []);

  const toggleSidebar = useCallback(() => setShowSidebar(!showSidebar), [showSidebar]);
  const clearError = useCallback(() => dispatch(clearMapError()), [dispatch]);

  const filteredServices = services.filter(service => {
    const matchesType = !selectedServiceType || service.type === selectedServiceType;
    const matchesSearch = !searchQuery || service.name.toLowerCase().includes(searchQuery.toLowerCase()) || service.address?.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesType && matchesSearch;
  });
  const filteredHotspots = hotspotFilter === 'all' ? hotspots : hotspots.filter(h => h.type === hotspotFilter);
  const filteredCameras = cameras.filter(camera => {
    const matchesFilter = cameraFilter === 'all' || camera.status === cameraFilter;
    const matchesRegion = !regionFilter || camera.region === regionFilter;
    return matchesFilter && matchesRegion;
  });

  const getServiceConfig = useCallback((type) => serviceTypes.find(st => st.id === type), [serviceTypes]);
  const formatDistance = (distance) => distance < 1 ? `${(distance * 1000).toFixed(0)} متر` : `${distance.toFixed(1)} کیلومتر`;

  return (
    <div className="map-page-full">
      <div className="map-top-bar">
        <div className="bar-left">
          <button className="menu-toggle-btn" onClick={toggleSidebar}>☰</button>
          <h1><span className="logo-icon">🗺️</span> نقشه خدمات هرمزگان</h1>
        </div>
        <div className="bar-center">
          <div className="tab-group">
            <button className={`tab-btn ${activeTab === 'services' ? 'active' : ''}`} onClick={() => setActiveTab('services')}>
              <span className="tab-icon">🏪</span> خدمات
            </button>
            <button className={`tab-btn ${activeTab === 'hotspots' ? 'active' : ''}`} onClick={() => setActiveTab('hotspots')}>
              <span className="tab-icon">🚨</span> حادثه‌خیز
              <span className="tab-badge">{hotspots.filter(h => h.status === 'active').length}</span>
            </button>
            <button className={`tab-btn ${activeTab === 'cameras' ? 'active' : ''}`} onClick={() => setActiveTab('cameras')}>
              <span className="tab-icon">📹</span> دوربین‌ها
              <span className="tab-badge">{cameras.filter(c => c.status === 'active').length}</span>
            </button>
          </div>
        </div>
        <div className="bar-right">
          <button className="locate-btn" onClick={handleGetLocation} disabled={isGeolocating}>
            {isGeolocating ? '⏳' : '📍'} موقعیت من
          </button>
          <button className="refresh-btn" onClick={() => window.location.reload()}>🔄</button>
        </div>
      </div>

      {mapError && (
        <div className="error-banner">
          <span className="error-icon">⚠️</span>
          <span className="error-text">{mapError}</span>
          <button className="error-close" onClick={clearError}>✕</button>
        </div>
      )}

      {mapLoading && (
        <div className="loading-overlay">
          <div className="loading-spinner"></div>
          <p>در حال بارگذاری...</p>
        </div>
      )}

      <div className="map-content-full">
        <div className={`map-sidebar-full ${showSidebar ? 'open' : 'closed'} ${isMobile ? 'mobile' : ''}`}>
          <div className="sidebar-header">
            <h3>{activeTab === 'services' && '🏪 خدمات'}{activeTab === 'hotspots' && '🚨 نقاط حادثه‌خیز'}{activeTab === 'cameras' && '📹 دوربین‌ها'}</h3>
            <span className="results-count">
              {activeTab === 'services' && filteredServices.length}
              {activeTab === 'hotspots' && filteredHotspots.length}
              {activeTab === 'cameras' && filteredCameras.length}
            </span>
            {isMobile && <button className="sidebar-close" onClick={toggleSidebar}>✕</button>}
          </div>
          <div className="sidebar-content">
            {activeTab === 'services' && (
              <>
                <MapSearch searchQuery={searchQuery} onSearchChange={(q) => dispatch(setSearchQuery(q))}
                  selectedServiceType={selectedServiceType} onServiceTypeChange={(type) => dispatch(setServiceTypeFilter(type))}
                  serviceTypes={serviceTypes} onSearch={handleSearch} />
                <div className="sidebar-list">
                  {filteredServices.length === 0 ? (
                    <div className="empty-state"><span className="empty-icon">🔍</span><p>نتیجه‌ای یافت نشد</p><p className="empty-subtitle">سایر فیلترها را امتحان کنید</p></div>
                  ) : (
                    filteredServices.map((service) => {
                      const config = getServiceConfig(service.type);
                      return (
                        <div key={service.id} className={`list-item ${selectedMarker?.id === service.id ? 'selected' : ''}`}
                          onClick={() => dispatch(selectMarker(service))}>
                          <div className="item-icon" style={{ color: config?.color }}>{config?.icon || '📍'}</div>
                          <div className="item-info">
                            <h4>{service.name}</h4>
                            <div className="item-meta">
                              <span>⭐ {service.rating}</span>
                              <span>📏 {formatDistance(service.distance)}</span>
                              <span className="item-type">{config?.name}</span>
                            </div>
                          </div>
                          <div className="item-actions">
                            <button className="action-btn-small" onClick={(e) => { e.stopPropagation(); handleGetDirections(service); }}>🧭</button>
                          </div>
                        </div>
                      );
                    })
                  )}
                </div>
              </>
            )}
            {activeTab === 'hotspots' && (
              <>
                <HotspotFilter hotspotFilter={hotspotFilter} onFilterChange={(f) => dispatch(setHotspotFilter(f))}
                  hotspotTypes={hotspotTypes} showHotspots={showHotspots} onToggleHotspots={() => dispatch(toggleHotspots())} />
                <HotspotList hotspots={filteredHotspots} selectedHotspot={selectedHotspot}
                  onHotspotSelect={(h) => dispatch(selectHotspot(h))} hotspotTypes={hotspotTypes} />
              </>
            )}
            {activeTab === 'cameras' && (
              <>
                <CameraFilter cameraFilter={cameraFilter} regionFilter={regionFilter}
                  onFilterChange={(f) => dispatch(setCameraFilter(f))} onRegionChange={(r) => dispatch(setRegionFilter(r))}
                  regions={regions} statuses={statuses} />
                <CameraList cameras={filteredCameras} selectedCamera={selectedCamera} onCameraSelect={(c) => dispatch(selectCamera(c))} />
              </>
            )}
          </div>
        </div>

        <div className="map-container-full">
          <LeafletMapContainer center={[center.lat, center.lng]} zoom={zoom} className="leaflet-map" whenReady={() => setMapLoaded(true)}>
            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution='&copy; OpenStreetMap contributors' />
            <MapUpdater center={center} zoom={zoom} />
            {mapLoaded && (
              <>
                {userLocation && (
                  <>
                    <Circle center={[userLocation.lat, userLocation.lng]} radius={50} pathOptions={{ color: '#3b82f6', fillColor: '#3b82f6', fillOpacity: 0.2, weight: 2 }} />
                    <Marker position={[userLocation.lat, userLocation.lng]}
                      icon={L.divIcon({ className: 'user-location-marker', html: '<div class="user-dot"><div class="user-pulse"></div></div>', iconSize: [24, 24], iconAnchor: [12, 12] })}>
                      <Popup><div className="user-popup"><h4>📍 موقعیت شما</h4><p>عرض: {userLocation.lat.toFixed(6)}</p><p>طول: {userLocation.lng.toFixed(6)}</p>
                        <button className="popup-btn" onClick={() => dispatch(setZoom(16))}>🔍 بزرگنمایی</button></div></Popup>
                    </Marker>
                  </>
                )}
                {activeTab === 'services' && <MapMarkers markers={filteredServices} selectedMarker={selectedMarker} onMarkerClick={(m) => dispatch(selectMarker(m))} serviceTypes={serviceTypes} onGetDirections={handleGetDirections} />}
                {activeTab === 'hotspots' && showHotspots && <HotspotMarkers hotspots={filteredHotspots} selectedHotspot={selectedHotspot} onHotspotClick={(h) => dispatch(selectHotspot(h))} hotspotTypes={hotspotTypes} />}
                {activeTab === 'cameras' && <CameraMarkers cameras={filteredCameras} selectedCamera={selectedCamera} onCameraClick={(c) => dispatch(selectCamera(c))} cameraTypes={cameraTypes} />}
                {isRouteActive && routeStart && routeEnd && (
                  <>
                    <Polyline positions={[[routeStart.lat, routeStart.lng], [routeEnd.lat, routeEnd.lng]]} pathOptions={{ color: '#667eea', weight: 4, opacity: 0.8, dashArray: '10, 10' }} />
                    <Popup position={[(routeStart.lat + routeEnd.lat) / 2, (routeStart.lng + routeEnd.lng) / 2]}>
                      <div className="route-popup"><h4>🗺️ اطلاعات مسیر</h4><p>📏 {routeInfo?.distance} کیلومتر</p><p>⏱️ {routeInfo?.duration} دقیقه</p>
                        <button className="popup-btn" onClick={clearRoute}>✕ بستن مسیر</button></div>
                    </Popup>
                  </>
                )}
                {filteredServices.length > 0 && activeTab === 'services' && <MapBounds markers={filteredServices} />}
              </>
            )}
          </LeafletMapContainer>

          <div className="map-controls">
            <button className="control-btn zoom-in" onClick={() => dispatch(setZoom(Math.min(zoom + 1, 18)))}>+</button>
            <button className="control-btn zoom-out" onClick={() => dispatch(setZoom(Math.max(zoom - 1, 3)))}>−</button>
            <button className="control-btn reset" onClick={() => { dispatch(setMapCenter({ lat: 27.2158, lng: 56.2808 })); dispatch(setZoom(13)); clearRoute(); }}>⌖</button>
          </div>

          <div className="map-info">
            <div className="info-item"><span className="info-label">📍 مرکز:</span><span className="info-value">{center.lat.toFixed(4)}, {center.lng.toFixed(4)}</span></div>
            <div className="info-item"><span className="info-label">🔍 زوم:</span><span className="info-value">{zoom}</span></div>
          </div>

          {isMobile && !showSidebar && <button className="mobile-sidebar-toggle" onClick={toggleSidebar}>☰</button>}
        </div>
      </div>

      {activeTab === 'services' && selectedMarker && (
        <div className="detail-panel service-detail">
          <button className="panel-close" onClick={() => dispatch(selectMarker(null))}>✕</button>
          <div className="panel-content">
            <div className="panel-header">
              <span className="panel-icon" style={{ color: getServiceConfig(selectedMarker.type)?.color }}>{getServiceConfig(selectedMarker.type)?.icon}</span>
              <h2>{selectedMarker.name}</h2>
            </div>
            <div className="panel-body">
              <div className="detail-grid">
                <div className="detail-item"><span className="detail-label">⭐ امتیاز</span><span className="detail-value">{selectedMarker.rating}/۵</span></div>
                <div className="detail-item"><span className="detail-label">📏 فاصله</span><span className="detail-value">{formatDistance(selectedMarker.distance)}</span></div>
                <div className="detail-item"><span className="detail-label">📍 آدرس</span><span className="detail-value">{selectedMarker.address}</span></div>
                <div className="detail-item"><span className="detail-label">📞 تلفن</span><a href={`tel:${selectedMarker.phone}`} className="detail-value link">{selectedMarker.phone}</a></div>
                <div className="detail-item"><span className="detail-label">🕐 ساعات کاری</span><span className="detail-value">{selectedMarker.openHours}</span></div>
                <div className="detail-item"><span className="detail-label">🏷️ نوع</span><span className="detail-value">{getServiceConfig(selectedMarker.type)?.name}</span></div>
              </div>
              <div className="panel-actions">
                <button className="action-btn primary" onClick={() => handleGetDirections(selectedMarker)}>🧭 مسیریابی</button>
                <a href={`tel:${selectedMarker.phone}`} className="action-btn">📞 تماس</a>
                <button className="action-btn">⭐ ذخیره</button>
                <button className="action-btn">📤 اشتراک</button>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'hotspots' && selectedHotspot && (
        <HotspotInfo hotspot={selectedHotspot} hotspotTypes={hotspotTypes} onClose={() => dispatch(clearHotspotSelection())}
          onReport={() => console.log('Reporting hotspot:', selectedHotspot.id)} />
      )}

      {activeTab === 'cameras' && selectedCamera && (
        <CameraInfo camera={selectedCamera} onClose={() => dispatch(clearCameraSelection())}
          onReportIssue={(id, msg) => console.log('Reporting camera issue:', id, msg)} />
      )}
    </div>
  );
};

export default MapPage;
