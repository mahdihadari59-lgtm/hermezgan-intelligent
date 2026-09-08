
import React from 'react';
import './HotspotFilter.css';

const HotspotFilter = ({ children, className, ...props }) => {
  return (
    <div className={`hotspotfilter-container ${className || ''}`} {...props}>
      {children}
    </div>
  );
};

export default HotspotFilter;
