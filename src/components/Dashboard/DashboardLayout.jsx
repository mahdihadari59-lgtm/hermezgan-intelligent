
import React from 'react';
import './DashboardLayout.css';

const DashboardLayout = ({ children, className, ...props }) => {
  return (
    <div className={`dashboardlayout-container ${className || ''}`} {...props}>
      {children}
    </div>
  );
};

export default DashboardLayout;
