import React from 'react';
import './Card.css';

const Card = ({ 
  children, 
  title = null, 
  icon = null,
  className = '',
  variant = 'default',
  onClick = null
}) => {
  const classes = [
    'card',
    `card-${variant}`,
    onClick ? 'card-clickable' : '',
    className
  ].filter(Boolean).join(' ');

  return (
    <div className={classes} onClick={onClick}>
      {(title || icon) && (
        <div className="card-header">
          {icon && <span className="card-icon">{icon}</span>}
          {title && <h3 className="card-title">{title}</h3>}
        </div>
      )}
      <div className="card-body">
        {children}
      </div>
    </div>
  );
};

export default Card;
