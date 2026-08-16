import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Layout.css';

const Layout = ({ children }) => {
  const location = useLocation();

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <div className="logo">
            <h1>🌊 هرمزگان هوشمند</h1>
          </div>
          <nav className="nav">
            <Link to="/" className={location.pathname === '/' ? 'active' : ''}>📊 داشبورد</Link>
            <Link to="/chat" className={location.pathname === '/chat' ? 'active' : ''}>💬 چت</Link>
            <Link to="/map" className={location.pathname === '/map' ? 'active' : ''}>🗺️ نقشه</Link>
          </nav>
        </div>
      </header>
      <div className="main-content">
        <div className="content">
          {children}
        </div>
      </div>
    </div>
  );
};

export default Layout;
