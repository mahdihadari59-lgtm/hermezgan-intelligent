
import React from 'react';
import './MessageList.css';

const MessageList = ({ children, className, ...props }) => {
  return (
    <div className={`messagelist-container ${className || ''}`} {...props}>
      {children}
    </div>
  );
};

export default MessageList;
