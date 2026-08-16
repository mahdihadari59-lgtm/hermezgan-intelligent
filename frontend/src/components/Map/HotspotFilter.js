import React from 'react';

const HotspotFilter = ({
  hotspotFilter,
  onFilterChange,
  hotspotTypes,
  showHotspots,
  onToggleHotspots,
}) => {
  return (
    <div className="hotspot-filter-wrapper">
      <div className="filter-header">
        <label className="toggle-hotspots">
          <input
            type="checkbox"
            checked={showHotspots}
            onChange={() => onToggleHotspots()}
          />
          <span className="toggle-label">🚨 نقاط حادثه‌خیز</span>
        </label>
      </div>

      {showHotspots && (
        <div className="filter-buttons">
          <button
            className={
