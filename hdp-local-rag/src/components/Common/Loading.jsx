
import React from 'react';
import './Loading.css';

const Loading = ({ children, className, ...props }) => {
  return (
    <div className={`loading-container ${className || ''}`} {...props}>
      {children}
    </div>
  );
};

export default Loading;
