import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { setSearchQuery, setServiceTypeFilter } from '../store/slices/mapSlice';
import mapService from '../services/mapService';
import useLocation from '../hooks/useLocation';
import { SERVICE_TYPES } from '../utils/constants';
import { formatDistance } from '../utils/helpers';
import './SearchPage.css';

const SearchPage = () => {
  const dispatch = useDispatch();
  const { searchQuery, selectedServiceType } = useSelector(state => state.map);
  const { location, getLocation } = useLocation();
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (location) handleSearch('');
  }, [location]);

  const handleSearch = async (query) => {
    const searchTerm = query || searchQuery;
    if (!searchTerm.trim() && !location) return;
    setIsLoading(true);
    try {
      const response = await mapService.searchLocations(searchTerm, location?.lat, location?.lng);
      setResults(response.results || []);
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="search-page">
      <div className="search-header"><h1>🔍 جستجوی خدمات</h1><p>خدمات مورد نیاز خود را در بندرعباس پیدا کنید</p></div>
      <div className="search-input-wrapper">
        <input type="text" value={searchQuery} onChange={(e) => dispatch(setSearchQuery(e.target.value))} placeholder="جستجو برای خدمات، مکان‌ها..." className="search-input" onKeyPress={(e) => e.key === 'Enter' && handleSearch()} />
        <button onClick={() => handleSearch()} className="search-button" disabled={isLoading}>{isLoading ? '⏳' : '🔍'}</button>
        <button onClick={getLocation} className="location-button" title="موقعیت من">📍</button>
      </div>
      <div className="filter-bar">
        <button className={`filter-chip ${!selectedServiceType ? 'active' : ''}`} onClick={() => { dispatch(setServiceTypeFilter(null)); handleSearch(); }}>همه</button>
        {SERVICE_TYPES.map((type) => (
          <button key={type.id} className={`filter-chip ${selectedServiceType === type.id ? 'active' : ''}`} onClick={() => { dispatch(setServiceTypeFilter(type.id)); handleSearch(); }}>
            <span className="filter-icon">{type.icon}</span>{type.name}
          </button>
        ))}
      </div>
      <div className="search-results">
        {isLoading ? <div className="loading-state">در حال جستجو...</div> : results.length === 0 ? <div className="empty-state"><span className="empty-icon">🔍</span><p>نتیجه‌ای یافت نشد</p></div> : (
          <div className="results-grid">
            {results.map((result) => (
              <div key={result.id} className="result-card">
                <div className="result-header"><span className="result-icon">{SERVICE_TYPES.find(t => t.id === result.type)?.icon || '📍'}</span><h3 className="result-name">{result.name}</h3></div>
                <div className="result-details"><p className="result-address">📍 {result.address}</p><div className="result-meta"><span>⭐ {result.rating}/۵</span>{result.distance && <span>📏 {formatDistance(result.distance)}</span>}</div></div>
                <div className="result-actions"><button className="action-btn">🧭 مسیریابی</button><a href={`tel:${result.phone}`} className="action-btn">📞 تماس</a></div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default SearchPage;
