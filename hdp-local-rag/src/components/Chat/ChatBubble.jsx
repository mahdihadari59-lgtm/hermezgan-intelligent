
import React from 'react';
import './ChatBubble.css';

const ChatBubble = ({ children, className, ...props }) => {
  return (
    <div className={`chatbubble-container ${className || ''}`} {...props}>
      {children}
    </div>
  );
};

export default ChatBubble;
