import React from 'react';
import './StatCards.css';

const StatCards = ({ stats }) => {
  const items = [
    { key: 'totalUsers', label: '👥 کل کاربران', value: stats.totalUsers, color: '#667eea' },
    { key: 'activeUsers', label: '🟢 کاربران فعال', value: stats.activeUsers, color: '#2ed573' },
    { key: 'totalServices', label: '🏢 خدمات', value: stats.totalServices, color: '#ffa502' },
    { key: 'totalChats', label: '💬 چت‌ها', value: stats.totalChats, color: '#1e90ff' }
  ];

  return (
    <div className="stat-cards">
      {items.map((item) => (
        <div key={item.key} className="stat-card" style={{ borderLeftColor: item.color }}>
          <div className="stat-card-header">
            <span className="stat-label">{item.label}</span>
          </div>
          <div className="stat-card-value" style={{ color: item.color }}>
            {item.value.toLocaleString('fa-IR')}
          </div>
        </div>
      ))}
    </div>
  );
};

export default StatCards;
