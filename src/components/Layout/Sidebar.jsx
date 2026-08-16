
import React from 'react';
import './Sidebar.css';

const Sidebar = ({ children, className, ...props }) => {
  return (
    <div className={`sidebar-container ${className || ''}`} {...props}>
      {children}
    </div>
  );
};

export default Sidebar;
