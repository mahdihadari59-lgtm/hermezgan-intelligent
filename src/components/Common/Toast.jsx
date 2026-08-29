
import React from 'react';
import './Toast.css';

const Toast = ({ children, className, ...props }) => {
  return (
    <div className={`toast-container ${className || ''}`} {...props}>
      {children}
    </div>
  );
};

export default Toast;
