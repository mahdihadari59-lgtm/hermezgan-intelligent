
import React from 'react';
import './MessageInput.css';

const MessageInput = ({ children, className, ...props }) => {
  return (
    <div className={`messageinput-container ${className || ''}`} {...props}>
      {children}
    </div>
  );
};

export default MessageInput;
