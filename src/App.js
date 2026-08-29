import React from 'react';
import { Provider } from 'react-redux';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import store from './store';
import HomePage from './pages/HomePage';
import ChatPage from './pages/ChatPage';
import MapPage from './pages/MapPage';
import DashboardPage from './pages/DashboardPage';
import './App.css';

function App() {
  return (
    <Provider store={store}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/map" element={<MapPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
        </Routes>
      </BrowserRouter>
    </Provider>
  );
}

export default App;
