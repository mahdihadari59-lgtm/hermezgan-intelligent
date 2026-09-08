
import React from 'react';
import './Charts.css';

const Charts = ({ children, className, ...props }) => {
  return (
    <div className={`charts-container ${className || ''}`} {...props}>
      {children}
    </div>
  );
};

export default Charts;
