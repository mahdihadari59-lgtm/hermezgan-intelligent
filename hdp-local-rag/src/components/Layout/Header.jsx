
import React from 'react';
import './Header.css';

const Header = ({ children, className, ...props }) => {
  return (
    <div className={`header-container ${className || ''}`} {...props}>
      {children}
    </div>
  );
};

export default Header;
