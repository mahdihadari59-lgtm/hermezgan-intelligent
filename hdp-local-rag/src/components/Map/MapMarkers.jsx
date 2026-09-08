
import React from 'react';
import './MapMarkers.css';

const MapMarkers = ({ children, className, ...props }) => {
  return (
    <div className={`mapmarkers-container ${className || ''}`} {...props}>
      {children}
    </div>
  );
};

export default MapMarkers;
