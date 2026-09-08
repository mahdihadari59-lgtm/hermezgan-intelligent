
import React from 'react';
import './TypingIndicator.css';

const TypingIndicator = ({ children, className, ...props }) => {
  return (
    <div className={`typingindicator-container ${className || ''}`} {...props}>
      {children}
    </div>
  );
};

export default TypingIndicator;
