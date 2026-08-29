import React from 'react';
import './Hotspots.css';

const HotspotList = ({ hotspots, selectedHotspot, onHotspotSelect, hotspotTypes }) => {
  const getHotspotConfig = (type) => {
    return hotspotTypes.find(ht => ht.id === type);
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high': return '#ff4757';
      case 'medium': return '#ffa502';
      case 'low': return '#2ed573';
      default: return '#667eea';
    }
  };

  return (
    <div className="hotspot-list-wrapper">
      <h3 className="list-title">🚨 نقاط حادثه‌خیز ({hotspots.length})</h3>
      <div className="hotspot-list">
        {hotspots.length === 0 ? (
          <div className="empty-list"><p>نقطه حادثه‌خیز یافت نشد</p></div>
        ) : (
          hotspots.map((hotspot) => {
            const config = getHotspotConfig(hotspot.type);
            const isSelected = selectedHotspot?.id === hotspot.id;
            return (
              <div key={hotspot.id} className={`hotspot-list-item ${isSelected ? 'selected' : ''}`} onClick={() => onHotspotSelect(hotspot)} style={{ borderLeftColor: config?.color }}>
                <div className="list-item-header">
                  <span className="list-item-icon">{config?.icon}</span>
                  <h4 className="list-item-title">{hotspot.title}</h4>
                </div>
                <div className="list-item-body">
                  <p className="list-item-description">{hotspot.description}</p>
                  <div className="list-item-meta">
                    <span className="severity-badge-small" style={{ backgroundColor: `${getSeverityColor(hotspot.severity)}20`, color: getSeverityColor(hotspot.severity) }}>
                      {hotspot.severity === 'high' ? '⚠️ بسیار خطرناک' : hotspot.severity === 'medium' ? '⚡ متوسط' : '✓ کم'}
                    </span>
                    <span className="time-badge">{hotspot.reportedAt}</span>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default HotspotList;
