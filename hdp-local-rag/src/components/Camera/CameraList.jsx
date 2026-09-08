
import React from 'react';
import './CameraList.css';

const CameraList = ({ children, className, ...props }) => {
  return (
    <div className={`cameralist-container ${className || ''}`} {...props}>
      {children}
    </div>
  );
};

export default CameraList;
