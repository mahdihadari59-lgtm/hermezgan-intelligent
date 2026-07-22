import React from 'react';
import { Marker, Popup, CircleMarker } from 'react-leaflet';
import L from 'leaflet';

const HotspotMarkers = ({ hotspots, selectedHotspot, onHotspotClick, hotspotTypes }) => {
  const getHotspotConfig = (type) => {
    return hotspotTypes.find(ht => ht.id === type);
  };

  const createHotspotIcon = (hotspot) => {
    const config = getHotspotConfig(hotspot.type);
    return L.divIcon({
      className: `hotspot-marker ${hotspot.type} ${hotspot.severity}`,
      html: `<div class="hotspot-pin" style="background-color: ${config?.color}; border-color: ${config?.color}">
        <span class="hotspot-icon">${config?.icon}</span>
        <div class="pulse"></div>
      </div>`,
      iconSize: [50, 50],
      iconAnchor: [25, 25],
      popupAnchor: [0, -25],
    });
  };

  return (
    <>
      {hotspots.map((hotspot) => {
        const config = getHotspotConfig(hotspot.type);
        const isSelected = selectedHotspot?.id === hotspot.id;

        return (
          <React.Fragment key={hotspot.id}>
            <Marker
              position={[hotspot.lat, hotspot.lng]}
              icon={createHotspotIcon(hotspot)}
              eventHandlers={{ click: () => onHotspotClick(hotspot) }}
              className={isSelected ? 'selected-hotspot' : ''}
            >
              <Popup className="hotspot-popup">
                <div className="popup-hotspot-content">
                  <div className="hotspot-popup-header">
                    <span className="hotspot-type-icon">{config?.icon}</span>
                    <h4>{hotspot.title}</h4>
                  </div>
                  <div className="hotspot-popup-body">
                    <p className="description">{hotspot.description}</p>
                    <div className="hotspot-meta">
                      <div className="meta-item">
                        <span className="meta-label">🔴 شدت:</span>
                        <span className="severity-badge" style={{ backgroundColor: `${config?.color}20`, color: config?.color }}>
                          {hotspot.severity === 'high' ? 'بسیار خطرناک' : hotspot.severity === 'medium' ? 'متوسط' : 'کم'}
                        </span>
                      </div>
                      <div className="meta-item">
                        <span className="meta-label">⏰ زمان:</span>
                        <span>{hotspot.reportedAt}</span>
                      </div>
                      <div className="meta-item">
                        <span className="meta-label">👤 منبع:</span>
                        <span>{hotspot.reportedBy}</span>
                      </div>
                      <div className="meta-item">
                        <span className="meta-label">✓ وضعیت:</span>
                        <span className="status-badge" style={{ backgroundColor: hotspot.status === 'active' ? '#ff475720' : '#2ed57320', color: hotspot.status === 'active' ? '#ff4757' : '#2ed573' }}>
                          {hotspot.status === 'active' ? 'فعال' : 'حل شده'}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </Popup>
            </Marker>
            {hotspot.severity === 'high' && (
              <CircleMarker
                center={[hotspot.lat, hotspot.lng]}
                radius={30}
                fill={true}
                fillColor={config?.color}
                fillOpacity={0.1}
                stroke={true}
                color={config?.color}
                weight={2}
                dashArray="5, 5"
                className="hotspot-danger-zone"
              />
            )}
          </React.Fragment>
        );
      })}
    </>
  );
};

export default HotspotMarkers;
