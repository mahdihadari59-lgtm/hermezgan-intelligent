
import React from 'react';
import './MapContainer.css';

const MapContainer = ({ children, className, ...props }) => {
  return (
    <div className={`mapcontainer-container ${className || ''}`} {...props}>
      {children}
    </div>
  );
};

export default MapContainer;
