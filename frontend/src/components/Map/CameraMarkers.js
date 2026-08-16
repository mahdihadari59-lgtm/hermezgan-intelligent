// src/components/Map/CameraMarkers.js
import React, { useMemo } from 'react';
import { Marker, Popup } from 'react-leaflet';
import L from 'leaflet';

const CameraMarkers = ({ cameras, selectedCamera, onCameraClick, cameraTypes }) => {
  // Get status color
  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return '#2ed573';
      case 'installing':
        return '#ffa502';
      case 'pending':
        return '#ff4757';
      default:
        return '#667eea';
    }
  };

  // Get status text
  const getStatusText = (status) => {
    switch (status) {
      case 'active':
        return '✅ فعال';
      case 'installing':
        return '⚠️ در حال نصب';
      case 'pending':
        return '🔴 نیاز فوری';
      default:
        return 'نامشخص';
    }
  };

  // Create camera icon
  const createCameraIcon = (camera, isSelected = false) => {
    const statusColor = getStatusColor(camera.status);
    const isActive = camera.status === 'active';
    const size = isSelected ? 50 : 40;

    return L.divIcon({
      className: `camera-marker ${camera.status} ${isSelected ? 'selected' : ''}`,
      html: `
        <div class="camera-pin" style="
          background: ${statusColor};
          width: ${size}px;
          height: ${size}px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          border: ${isSelected ? '4px' : '3px'} solid white;
          box-shadow: ${isSelected ? '0 0 20px rgba(102,126,234,0.6)' : '0 2px 8px rgba(0,0,0,0.15)'};
          transition: all 0.3s ease;
          font-size: ${isSelected ? '22px' : '18px'};
          position: relative;
        ">
          <span class="camera-icon">📹</span>
          ${isActive ? `
            <div class="camera-status-dot" style="
              position: absolute;
              top: -4px;
              right: -4px;
              width: 12px;
              height: 12px;
              background: #2ed573;
              border-radius: 50%;
              border: 2px solid white;
              animation: pulse-dot 2s ease-in-out infinite;
            "></div>
          ` : ''}
          ${camera.status === 'pending' ? `
            <div class="camera-alert" style="
              position: absolute;
              top: -4px;
              right: -4px;
              width: 12px;
              height: 12px;
              background: #ff4757;
              border-radius: 50%;
              border: 2px solid white;
              animation: pulse-alert 1s ease-in-out infinite;
            "></div>
          ` : ''}
        </div>
        <style>
          @keyframes pulse-dot {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.3); }
          }
          @keyframes pulse-alert {
            0%, 100% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.5); opacity: 0.5; }
          }
        </style>
      `,
      iconSize: [size, size],
      iconAnchor: [size/2, size/2],
      popupAnchor: [0, -size/2],
    });
  };

  // Memoize markers
  const memoizedMarkers = useMemo(() => {
    return cameras.map((camera) => {
      const isSelected = selectedCamera?.id === camera.id;
      const icon = createCameraIcon(camera, isSelected);

      return (
        <Marker
          key={camera.id}
          position={[camera.lat, camera.lng]}
          icon={icon}
          eventHandlers={{
            click: () => onCameraClick(camera),
          }}
          zIndexOffset={isSelected ? 1000 : 0}
        >
          <Popup className="camera-popup" closeButton={false}>
            <div className="popup-content">
              <div className="popup-header" style={{ borderBottomColor: getStatusColor(camera.status) }}>
                <span className="popup-icon">📹</span>
                <h4>{camera.name}</h4>
              </div>
              <div className="popup-body">
                <div className="popup-row">
                  <span>📊</span>
                  <span className="status-badge" style={{ color: getStatusColor(camera.status) }}>
                    {getStatusText(camera.status)}
                  </span>
                </div>
                {camera.types && (
                  <div className="popup-row">
                    <span>🎯</span>
                    <span>{camera.types.join('، ')}</span>
                  </div>
                )}
                {camera.installed && (
                  <div className="popup-row">
                    <span>📅</span>
                    <span>{camera.installed}</span>
                  </div>
                )}
                {camera.priority && (
                  <div className="popup-row">
                    <span>⚠️</span>
                    <span style={{ color: '#ff4757', fontWeight: 'bold' }}>
                      اولویت: {camera.priority}
                    </span>
                  </div>
                )}
              </div>
              <div className="popup-footer">
                <button className="popup-btn" style={{ background: getStatusColor(camera.status) }}>
                  🚨 گزارش مشکل
                </button>
              </div>
            </div>
          </Popup>
        </Marker>
      );
    });
  }, [cameras, selectedCamera, onCameraClick, createCameraIcon]);

  return <>{memoizedMarkers}</>;
};

export default CameraMarkers;
