// src/components/Map/MapSearch.js
import React, { useState, useRef, useEffect } from 'react';
import './MapSearch.css';

const MapSearch = ({
  searchQuery,
  onSearchChange,
  selectedServiceType,
  onServiceTypeChange,
  serviceTypes,
  onSearch,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isFocused, setIsFocused] = useState(false);
  const inputRef = useRef(null);

  // Handle search submit
  const handleSubmit = (e) => {
    e.preventDefault();
    if (onSearch) onSearch();
    setIsExpanded(false);
  };

  // Handle keyboard shortcut (Ctrl+K or Cmd+K)
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        inputRef.current?.focus();
      }
      if (e.key === 'Escape') {
        inputRef.current?.blur();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <div className="map-search-container">
      {/* Search Form */}
      <form className="search-form" onSubmit={handleSubmit}>
        <div className={`search-input-wrapper ${isFocused ? 'focused' : ''}`}>
          <span className="search-icon">🔍</span>
          <input
            ref={inputRef}
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            placeholder="جستجو برای خدمات... (Ctrl+K)"
            className="search-input"
            dir="rtl"
          />
          {searchQuery && (
            <button
              type="button"
              className="clear-btn"
              onClick={() => onSearchChange('')}
              title="پاک کردن"
            >
              ✕
            </button>
          )}
          <kbd className="search-shortcut">Ctrl+K</kbd>
        </div>
        <button type="submit" className="search-btn" title="جستجو">
          🔍
        </button>
      </form>

      {/* Service Type Filters */}
      <div className="service-filters">
        <button
          className={`filter-btn ${!selectedServiceType ? 'active' : ''}`}
          onClick={() => onServiceTypeChange(null)}
        >
          <span className="filter-icon">📌</span>
          <span className="filter-label">همه</span>
        </button>
        {serviceTypes?.map((service) => (
          <button
            key={service.id}
            className={`filter-btn ${selectedServiceType === service.id ? 'active' : ''}`}
            onClick={() => onServiceTypeChange(service.id)}
            style={{
              borderColor: selectedServiceType === service.id ? service.color : '#e9ecef',
              color: selectedServiceType === service.id ? service.color : '#718096',
            }}
            title={service.name}
          >
            <span className="filter-icon">{service.icon}</span>
            <span className="filter-label">{service.name}</span>
            {selectedServiceType === service.id && (
              <span className="filter-check">✓</span>
            )}
          </button>
        ))}
      </div>

      {/* Search Stats */}
      {searchQuery && (
        <div className="search-stats">
          <span>نتایج جستجو برای: <strong>"{searchQuery}"</strong></span>
        </div>
      )}
    </div>
  );
};

export default MapSearch;
