import React from 'react';

const CameraList = ({ cameras, selectedCamera, onCameraSelect }) => {
  const getStatusBadge = (status) => {
    switch (status) {
      case 'active': return { text: '✅ فعال', color: '#2ed573' };
      case 'installing': return { text: '⚠️ در حال نصب', color: '#ffa502' };
      case 'pending': return { text: '🔴 نیاز فوری', color: '#ff4757' };
      default: return { text: 'نامشخص', color: '#667eea' };
    }
  };

  return (
    <div className="camera-list-wrapper">
      <h3 className="list-title">📹 دوربین‌ها ({cameras.length})</h3>
      <div className="camera-list">
        {cameras.length === 0 ? (
          <div className="empty-list">دوربینی یافت نشد</div>
        ) : (
          cameras.map((camera) => {
            const badge = getStatusBadge(camera.status);
            const isSelected = selectedCamera?.id === camera.id;
            return (
              <div key={camera.id} className={`camera-list-item ${isSelected ? 'selected' : ''}`} onClick={() => onCameraSelect(camera)}>
                <div className="item-header">
                  <span className="item-icon">📹</span>
                  <h4 className="item-title">{camera.name}</h4>
                </div>
                <div className="item-meta">
                  <span className="status-badge" style={{ backgroundColor: `${badge.color}20`, color: badge.color }}>{badge.text}</span>
                  {camera.types && (
                    <div className="types-list">
                      {camera.types.map((type, idx) => <span key={idx} className="type-tag">{type}</span>)}
                    </div>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default CameraList;
