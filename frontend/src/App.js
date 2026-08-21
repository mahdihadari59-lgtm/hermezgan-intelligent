// ============================================================
// 1. src/App.js - کامپوننت اصلی React
// ============================================================
// مسیر: frontend/src/App.js

import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { Header, Sidebar, Footer } from './components/Layout';
import ChatPage from './pages/ChatPage';
import MapPage from './pages/MapPage';
import DashboardPage from './pages/DashboardPage';
import './App.css';

function App() {
  const ui = useSelector((state) => state.ui) || { isDarkMode: false };
  const { isDarkMode } = ui;

  return (
    <Router>
      <div className={`app ${isDarkMode ? 'dark-mode' : 'light-mode'}`}>
        <Header />
        <div className="app-container">
          <Sidebar />
          <main className="app-main">
            <Routes>
              <Route path="/" element={<div className="page-placeholder">🏠 صفحه اصلی</div>} />
              <Route path="/chat" element={<ChatPage />} />
              <Route path="/map" element={<MapPage />} />
              <Route path="/dashboard" element={<DashboardPage />} />
            </Routes>
          </main>
        </div>
        <Footer />
      </div>
    </Router>
  );
}

export default App;
