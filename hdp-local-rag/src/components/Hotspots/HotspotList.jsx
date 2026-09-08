
import React from 'react';
import './HotspotList.css';

const HotspotList = ({ children, className, ...props }) => {
  return (
    <div className={`hotspotlist-container ${className || ''}`} {...props}>
      {children}
    </div>
  );
};

export default HotspotList;
