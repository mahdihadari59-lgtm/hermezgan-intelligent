// src/components/Map/MapMarkers.js
import React, { useMemo } from 'react';
import { Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import { useSelector } from 'react-redux';

const MapMarkers = ({ markers, selectedMarker, onMarkerClick, serviceTypes }) => {
  // Create custom icon based on service type
  const createCustomIcon = (serviceType, isSelected = false) => {
    const serviceConfig = serviceTypes?.find(st => st.id === serviceType);
    const color = serviceConfig?.color || '#667eea';
    const icon = serviceConfig?.icon || '📍';
    const size = isSelected ? 48 : 40;

    return L.divIcon({
      className: `custom-marker ${serviceType} ${isSelected ? 'selected' : ''}`,
      html: `
        <div class="marker-content" style="
          background: ${color};
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
          color: white;
          transform: ${isSelected ? 'scale(1.15)' : 'scale(1)'};
        ">
          <span class="marker-icon">${icon}</span>
          ${isSelected ? '<div class="selected-ring"></div>' : ''}
        </div>
        <style>
          .selected-ring {
            position: absolute;
            top: -8px;
            left: -8px;
            right: -8px;
            bottom: -8px;
            border-radius: 50%;
            border: 2px solid ${color};
            animation: ring-pulse 1.5s ease-out infinite;
          }
          @keyframes ring-pulse {
            0% { transform: scale(1); opacity: 0.8; }
            100% { transform: scale(1.3); opacity: 0; }
          }
        </style>
      `,
      iconSize: [size, size],
      iconAnchor: [size/2, size/2],
      popupAnchor: [0, -size/2],
    });
  };

  // Memoize markers to prevent unnecessary re-renders
  const memoizedMarkers = useMemo(() => {
    return markers.map((marker) => {
      const isSelected = selectedMarker?.id === marker.id;
      const icon = createCustomIcon(marker.type, isSelected);

      return (
        <Marker
          key={marker.id}
          position={[marker.lat, marker.lng]}
          icon={icon}
          eventHandlers={{
            click: () => onMarkerClick(marker),
          }}
          zIndexOffset={isSelected ? 1000 : 0}
        >
          <Popup className="custom-popup" closeButton={false}>
            <div className="popup-content">
              <div className="popup-header">
                <span className="popup-icon">
                  {serviceTypes?.find(st => st.id === marker.type)?.icon || '📍'}
                </span>
                <h4>{marker.name}</h4>
              </div>
              <div className="popup-body">
                <div className="popup-row">
                  <span>⭐</span>
                  <span>{marker.rating}/۵</span>
                </div>
                <div className="popup-row">
                  <span>📏</span>
                  <span>{marker.distance} کیلومتر</span>
                </div>
                <div className="popup-row">
                  <span>📍</span>
                  <span>{marker.address}</span>
                </div>
                <div className="popup-row">
                  <span>📱</span>
                  <a href={`tel:${marker.phone}`}>{marker.phone}</a>
                </div>
                <div className="popup-row">
                  <span>🕐</span>
                  <span>{marker.openHours}</span>
                </div>
              </div>
              <div className="popup-footer">
                <button 
                  className="popup-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    // Handle directions
                  }}
                >
                  🧭 مسیریابی
                </button>
              </div>
            </div>
          </Popup>
        </Marker>
      );
    });
  }, [markers, selectedMarker, onMarkerClick, serviceTypes, createCustomIcon]);

  return <>{memoizedMarkers}</>;
};

export default MapMarkers;
