
import React from 'react';
import './Modal.css';

const Modal = ({ children, className, ...props }) => {
  return (
    <div className={`modal-container ${className || ''}`} {...props}>
      {children}
    </div>
  );
};

export default Modal;
