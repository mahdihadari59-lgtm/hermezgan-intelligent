import React from 'react';
import { Link } from 'react-router-dom';
import './HomePage.css';

const HomePage = () => {
  const features = [
    { icon: '💬', title: 'چت‌بات هوشمند', description: 'پرسش و پاسخ هوشمند با دستیار مجازی هرمزگان', link: '/chat', color: '#667eea' },
    { icon: '🗺️', title: 'نقشه تعاملی', description: 'نمایش خدمات و نقاط حادثه‌خیز روی نقشه', link: '/map', color: '#2ed573' },
    { icon: '📊', title: 'داشبورد تحلیلی', description: 'آمار و گزارش‌های عملکرد سیستم', link: '/dashboard', color: '#ffa502' },
    { icon: '📍', title: 'جستجوی مکان‌بنیان', description: 'جستجوی خدمات نزدیک به موقعیت شما', link: '/search', color: '#1e90ff' },
  ];

  return (
    <div className="home-page">
      <section className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">🌊 به هرمزگان هوشمند خوش آمدید</h1>
          <p className="hero-subtitle">سیستم دانش‌گراف هوشمند شهر بندرعباس</p>
          <div className="hero-actions">
            <Link to="/chat" className="btn btn-primary">شروع کنید</Link>
            <Link to="/map" className="btn btn-secondary">نقشه را ببینید</Link>
          </div>
        </div>
      </section>
      <section className="features-section">
        <h2 className="section-title">خدمات ما</h2>
        <div className="features-grid">
          {features.map((feature, index) => (
            <Link to={feature.link} key={index} className="feature-card">
              <div className="feature-icon" style={{ backgroundColor: feature.color }}>{feature.icon}</div>
              <h3 className="feature-title">{feature.title}</h3>
              <p className="feature-description">{feature.description}</p>
              <span className="feature-link">بیشتر بدانید →</span>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
};

export default HomePage;
