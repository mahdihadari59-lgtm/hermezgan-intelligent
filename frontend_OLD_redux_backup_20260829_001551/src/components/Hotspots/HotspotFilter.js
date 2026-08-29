import React from 'react';
import './Hotspots.css';

const HotspotFilter = ({ hotspotFilter, onFilterChange, hotspotTypes, showHotspots, onToggleHotspots }) => {
  return (
    <div className="hotspot-filter-wrapper">
      <div className="filter-header">
        <label className="toggle-hotspots">
          <input type="checkbox" checked={showHotspots} onChange={() => onToggleHotspots()} />
          <span className="toggle-label">نقاط حادثه‌خیز</span>
        </label>
      </div>
      {showHotspots && (
        <div className="filter-buttons">
          <button className={`filter-btn ${hotspotFilter === 'all' ? 'active' : ''}`} onClick={() => onFilterChange('all')}>همه</button>
          {hotspotTypes.map((type) => (
            <button key={type.id} className={`filter-btn ${hotspotFilter === type.id ? 'active' : ''}`} onClick={() => onFilterChange(type.id)} style={{ borderColor: hotspotFilter === type.id ? type.color : '#e9ecef', color: hotspotFilter === type.id ? type.color : '#718096' }}>
              <span className="btn-icon">{type.icon}</span>
              <span className="btn-label">{type.name}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

export default HotspotFilter;
