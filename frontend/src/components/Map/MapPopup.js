// src/components/Map/MapPopup.js
import React, { useState } from 'react';
import './MapPopup.css';

const MapPopup = ({ service, onClose, onGetDirections }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!service) return null;

  const serviceIcons = {
    hospital: '🏥',
    restaurant: '🍽️',
    taxi: '🚗',
    pharmacy: '💊',
    school: '🎓',
  };

  // Render stars
  const renderStars = (rating) => {
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);

    return (
      <div className="stars">
        {[...Array(fullStars)].map((_, i) => (
          <span key={`full-${i}`} className="star filled">★</span>
        ))}
        {hasHalfStar && <span className="star half">★</span>}
        {[...Array(emptyStars)].map((_, i) => (
          <span key={`empty-${i}`} className="star empty">★</span>
        ))}
        <span className="rating-number">{rating.toFixed(1)}</span>
      </div>
    );
  };

  // Get service type label
  const getServiceTypeLabel = (type) => {
    const labels = {
      hospital: 'بیمارستان',
      restaurant: 'رستوران',
      taxi: 'تاکسی',
      pharmacy: 'داروخانه',
      school: 'مدرسه',
    };
    return labels[type] || type;
  };

  return (
    <div className={`map-popup ${isExpanded ? 'expanded' : ''}`}>
      {/* Header */}
      <div className="popup-header">
        <div className="popup-header-left">
          <span className="service-icon">
            {serviceIcons[service.type] || '📍'}
          </span>
          <div className="service-title">
            <h3>{service.name}</h3>
            <span className="service-type">{getServiceTypeLabel(service.type)}</span>
          </div>
        </div>
        <div className="popup-header-actions">
          <button 
            className="popup-close"
            onClick={onClose}
            title="بستن"
          >
            ✕
          </button>
        </div>
      </div>

      {/* Body */}
      <div className="popup-body">
        {/* Rating */}
        <div className="rating-section">
          {renderStars(service.rating)}
        </div>

        {/* Info Grid */}
        <div className="info-grid">
          <div className="info-item">
            <span className="info-icon">📍</span>
            <div className="info-content">
              <span className="info-label">آدرس</span>
              <span className="info-value">{service.address}</span>
            </div>
          </div>

          <div className="info-item">
            <span className="info-icon">📱</span>
            <div className="info-content">
              <span className="info-label">تلفن</span>
              <a href={`tel:${service.phone}`} className="info-value link">
                {service.phone}
              </a>
            </div>
          </div>

          <div className="info-item">
            <span className="info-icon">🕐</span>
            <div className="info-content">
              <span className="info-label">ساعات کاری</span>
              <span className="info-value">{service.openHours}</span>
            </div>
          </div>

          <div className="info-item">
            <span className="info-icon">📏</span>
            <div className="info-content">
              <span className="info-label">فاصله</span>
              <span className="info-value">{service.distance} کیلومتر</span>
            </div>
          </div>
        </div>

        {/* Expandable Details */}
        {service.amenities && service.amenities.length > 0 && (
          <div className="popup-details">
            <button 
              className="details-toggle"
              onClick={() => setIsExpanded(!isExpanded)}
            >
              {isExpanded ? '▼ کمتر' : '▶ بیشتر'} 
              <span className="details-count">({service.amenities.length} امکانات)</span>
            </button>
            {isExpanded && (
              <div className="details-content">
                <ul className="amenities-list">
                  {service.amenities.map((item, idx) => (
                    <li key={idx} className="amenity-item">
                      <span className="amenity-check">✓</span>
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Footer Actions */}
      <div className="popup-footer">
        <button 
          className="action-btn primary"
          onClick={() => onGetDirections(service)}
        >
          🧭 مسیریابی
        </button>
        <button className="action-btn" onClick={() => window.location.href = `tel:${service.phone}`}>
          📞 تماس
        </button>
        <button className="action-btn">
          ⭐ ذخیره
        </button>
      </div>
    </div>
  );
};

export default MapPopup;
