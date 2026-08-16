
import React from 'react';
import './MapSearch.css';

const MapSearch = ({ children, className, ...props }) => {
  return (
    <div className={`mapsearch-container ${className || ''}`} {...props}>
      {children}
    </div>
  );
};

export default MapSearch;
