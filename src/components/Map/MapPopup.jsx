
import React from 'react';
import './MapPopup.css';

const MapPopup = ({ children, className, ...props }) => {
  return (
    <div className={`mappopup-container ${className || ''}`} {...props}>
      {children}
    </div>
  );
};

export default MapPopup;
