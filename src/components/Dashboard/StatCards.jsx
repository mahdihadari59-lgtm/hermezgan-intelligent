
import React from 'react';
import './StatCards.css';

const StatCards = ({ children, className, ...props }) => {
  return (
    <div className={`statcards-container ${className || ''}`} {...props}>
      {children}
    </div>
  );
};

export default StatCards;
