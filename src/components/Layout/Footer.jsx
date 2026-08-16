
import React from 'react';
import './Footer.css';

const Footer = ({ children, className, ...props }) => {
  return (
    <div className={`footer-container ${className || ''}`} {...props}>
      {children}
    </div>
  );
};

export default Footer;
