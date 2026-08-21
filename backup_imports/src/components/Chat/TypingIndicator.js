import React from 'react';
import './TypingIndicator.css';

const TypingIndicator = () => {
  return (
    <div
      className="typing-indicator"
      role="status"
      aria-label="ربات در حال تایپ است"
    >
      <div className="typing-dot"></div>
      <div className="typing-dot"></div>
      <div className="typing-dot"></div>
    </div>
  );
};

export default TypingIndicator;
