import React, { useState } from 'react';

const CameraInfo = ({ camera, onClose, onReportIssue }) => {
  const [reportMessage, setReportMessage] = useState('');
  if (!camera) return null;

  const getStatusInfo = (status) => {
    switch (status) {
      case 'active': return { text: '✅ فعال', color: '#2ed573' };
      case 'installing': return { text: '⚠️ در حال نصب', color: '#ffa502' };
      case 'pending': return { text: '🔴 نیاز فوری', color: '#ff4757' };
      default: return { text: 'نامشخص', color: '#667eea' };
    }
  };

  const statusInfo = getStatusInfo(camera.status);

  return (
    <div className="camera-info-panel">
      <button className="close-btn" onClick={onClose}>✕</button>
      <div className="info-header" style={{ borderColor: statusInfo.color }}>
        <span className="header-icon">📹</span>
        <h2>{camera.name}</h2>
      </div>
      <div className="info-body">
        <div className="status-section">
          <span className="status-badge-large" style={{ backgroundColor: `${statusInfo.color}20`, color: statusInfo.color, borderColor: statusInfo.color }}>{statusInfo.text}</span>
        </div>
        <div className="details-grid">
          <div className="detail-item"><span className="detail-icon">📍</span><div><span className="detail-label">موقعیت</span><span className="detail-value">{camera.lat}, {camera.lng}</span></div></div>
          {camera.types && (
            <div className="detail-item"><span className="detail-icon">🎯</span><div><span className="detail-label">نوع</span><span className="detail-value">{camera.types.join('، ')}</span></div></div>
          )}
        </div>
        <div className="info-actions">
          <button className="action-btn primary">📱 پشتیبانی</button>
          <button className="action-btn">📊 آمار</button>
        </div>
      </div>
    </div>
  );
};

export default CameraInfo;
