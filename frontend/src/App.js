import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

import ChatPage from './pages/ChatPage';

import './App.css';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/chat" replace />} />
      <Route path="/chat" element={<ChatPage />} />
    </Routes>
  );
}

export default App;
