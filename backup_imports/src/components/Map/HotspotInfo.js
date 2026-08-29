import React from 'react';
import './HotspotInfo.css';

const HotspotInfo = ({ hotspot, hotspotTypes, onClose, onReport }) => {
  if (!hotspot) return null;

  const getHotspotConfig = (type) => {
    return hotspotTypes.find(ht => ht.id === type);
  };

  const config = getHotspotConfig(hotspot.type);

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high': return '#ff4757';
      case 'medium': return '#ffa502';
      case 'low': return '#2ed573';
      default: return '#667eea';
    }
  };

  const getSeverityText = (severity) => {
    switch (severity) {
      case 'high': return 'بسیار خطرناک';
      case 'medium': return 'متوسط';
      case 'low': return 'کم';
      default: return 'نامشخص';
    }
  };

  return (
    <div className="hotspot-info-panel">
      <button className="close-btn" onClick={onClose}>✕</button>
      <div className="info-header">
        <span className="info-icon" style={{ color: config?.color }}>{config?.icon}</span>
        <h2 className="info-title">{hotspot.title}</h2>
      </div>
      <div className="info-body">
        <div className="severity-section">
          <div className="severity-badge-large" style={{ backgroundColor: `${getSeverityColor(hotspot.severity)}20`, borderLeft: `4px solid ${getSeverityColor(hotspot.severity)}` }}>
            <span className="severity-dot" style={{ backgroundColor: getSeverityColor(hotspot.severity) }}></span>
            <span>{getSeverityText(hotspot.severity)}</span>
          </div>
        </div>
        <div className="info-section">
          <h4>توضیحات</h4>
          <p>{hotspot.description}</p>
        </div>
        <div className="details-grid">
          <div className="detail-item">
            <span className="detail-icon">📍</span>
            <div className="detail-content">
              <span className="detail-label">موقعیت</span>
              <span className="detail-value">{hotspot.lat.toFixed(4)}, {hotspot.lng.toFixed(4)}</span>
            </div>
          </div>
          <div className="detail-item">
            <span className="detail-icon">⏰</span>
            <div className="detail-content">
              <span className="detail-label">زمان گزارش</span>
              <span className="detail-value">{hotspot.reportedAt}</span>
            </div>
          </div>
          <div className="detail-item">
            <span className="detail-icon">👤</span>
            <div className="detail-content">
              <span className="detail-label">منبع گزارش</span>
              <span className="detail-value">{hotspot.reportedBy}</span>
            </div>
          </div>
          <div className="detail-item">
            <span className="detail-icon">✓</span>
            <div className="detail-content">
              <span className="detail-label">وضعیت</span>
              <span className="detail-value" style={{ color: hotspot.status === 'active' ? '#ff4757' : '#2ed573' }}>
                {hotspot.status === 'active' ? 'فعال' : 'حل شده'}
              </span>
            </div>
          </div>
        </div>
        <div className="type-info">
          <h4>نوع حادثه</h4>
          <div className="type-tag" style={{ backgroundColor: `${config?.color}20`, color: config?.color, borderColor: config?.color }}>
            {config?.name}
          </div>
        </div>
        <div className="info-actions">
          <button className="action-btn primary">🚨 گزارش مسیر جایگزین</button>
          <button className="action-btn">⭐ ذخیره</button>
          <button className="action-btn">📱 اشتراک</button>
        </div>
        <div className="related-section">
          <h4>نقاط خطرناک نزدیک</h4>
          <p className="related-info">۲ نقطه دیگر در نزدیکی این مکان</p>
        </div>
      </div>
    </div>
  );
};

export default HotspotInfo;
