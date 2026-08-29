
import React from 'react';
import './CameraInfo.css';

const CameraInfo = ({ children, className, ...props }) => {
  return (
    <div className={`camerainfo-container ${className || ''}`} {...props}>
      {children}
    </div>
  );
};

export default CameraInfo;
