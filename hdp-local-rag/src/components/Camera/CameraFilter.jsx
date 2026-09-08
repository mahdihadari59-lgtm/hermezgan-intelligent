
import React from 'react';
import './CameraFilter.css';

const CameraFilter = ({ children, className, ...props }) => {
  return (
    <div className={`camerafilter-container ${className || ''}`} {...props}>
      {children}
    </div>
  );
};

export default CameraFilter;
