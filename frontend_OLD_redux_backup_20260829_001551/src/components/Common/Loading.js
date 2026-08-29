import React from 'react';
import './Loading.css';

const Loading = ({ size = 'medium', color = '#667eea', text = 'در حال بارگذاری...' }) => {
  const sizeMap = {
    small: '24px',
    medium: '40px',
    large: '56px'
  };

  return (
    <div className="loading-container">
      <div 
        className="loading-spinner" 
        style={{ 
          width: sizeMap[size], 
          height: sizeMap[size],
          borderColor: `${color}20`,
          borderTopColor: color
        }}
      />
      {text && <p className="loading-text">{text}</p>}
    </div>
  );
};

export default Loading;
