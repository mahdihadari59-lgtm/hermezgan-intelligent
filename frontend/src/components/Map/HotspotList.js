import React from 'react';

const HotspotList = ({ hotspots, selectedHotspot, onHotspotSelect, hotspotTypes }) => {
  const getHotspotConfig = (type) => {
    return hotspotTypes?.find(ht => ht.id === type);
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high':
        return '#ff4757';
      case 'medium':
        return '#ffa502';
      case 'low':
        return '#2ed573';
      default:
        return '#667eea';
    }
  };

  const getSeverityText = (severity) => {
    switch (severity) {
      case 'high':
        return '⚠️ بسیار خطرناک';
      case 'medium':
        return '⚡ متوسط';
      case 'low':
        return '✅ کم';
      default:
        return 'نامشخص';
    }
  };

  return (
    <div className="hotspot-list-wrapper">
      <h3 className="list-title">🚨 نقاط حادثه‌خیز ({hotspots?.length || 0})</h3>
      <div className="hotspot-list">
          <div className="empty-list">
            <p>نقطه حادثه‌خیزی یافت نشد</p>
          </div>
        ) : (
          hotspots.map((hotspot) => {
            const config = getHotspotConfig(hotspot.type);
            const isSelected = selectedHotspot?.id === hotspot.id;

            return (
              <div
                key={hotspot.id}
                className={
