import React from 'react';

const CameraFilter = ({ cameraFilter, regionFilter, onFilterChange, onRegionChange, regions, statuses }) => {
  return (
    <div className="camera-filter-wrapper">
      <h3 className="filter-title">📹 دوربین‌های نظارتی</h3>
      <div className="filter-section">
        <p className="section-label">وضعیت</p>
        <div className="filter-buttons">
          <button className={`filter-btn ${cameraFilter === 'all' ? 'active' : ''}`} onClick={() => onFilterChange('all')}>همه</button>
          {statuses.map((status) => (
            <button key={status.id} className={`filter-btn ${cameraFilter === status.id ? 'active' : ''}`} onClick={() => onFilterChange(status.id)} style={{ borderColor: cameraFilter === status.id ? status.color : '#e9ecef', color: cameraFilter === status.id ? status.color : '#718096' }}>
              {status.name}
            </button>
          ))}
        </div>
      </div>
      <div className="filter-section">
        <p className="section-label">منطقه</p>
        <select value={regionFilter || ''} onChange={(e) => onRegionChange(e.target.value || null)} className="region-select">
          <option value="">تمام مناطق</option>
          {regions.map((region) => (
            <option key={region.id} value={region.id}>{region.name} ({region.total})</option>
          ))}
        </select>
      </div>
    </div>
  );
};

export default CameraFilter;
