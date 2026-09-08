
import React from 'react';
import './Button.css';

const Button = ({ children, className, ...props }) => {
  return (
    <div className={`button-container ${className || ''}`} {...props}>
      {children}
    </div>
  );
};

export default Button;
