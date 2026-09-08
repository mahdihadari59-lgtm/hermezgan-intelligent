
import React from 'react';
import './ChatBox.css';

const ChatBox = ({ children, className, ...props }) => {
  return (
    <div className={`chatbox-container ${className || ''}`} {...props}>
      {children}
    </div>
  );
};

export default ChatBox;
