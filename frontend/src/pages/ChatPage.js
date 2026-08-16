// src/pages/ChatPage.js
import React, { useEffect } from 'react';
import {
  useDispatch,
  useSelector
} from 'react-redux';
import chatService from '../services/chatService';
import './ChatPage.css';

import { addMessage, clearMessages, setSessionId, setTyping } from '../features/chat/chatSlice';
import { addNotification, addToast, clearError, setError, setLoading } from '../features/ui/uiSlice';
import ChatBox from '../components/ChatBox';

const ChatPage = () => {
  const dispatch = useDispatch();
  const { messages, isLoading, isTyping, sessionId } = useSelector(state => state.chat);
  const { userLocation } = useSelector(state => state.map);
  const { theme } = useSelector(state => state.ui);

  // Initialize chat
  useEffect(() => {
    dispatch(clearMessages());
    
    // Generate session ID if not exists
    if (!sessionId) {
      const newSessionId = `chat_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      dispatch(setSessionId(newSessionId));
    }

    // Welcome message
    dispatch(addMessage({
      text: '🌊 سلام! من دستیار هوشمند هرمزگان هستم. چگونه می‌تونم کمکتون کنم؟',
      sender: 'bot',
      timestamp: Date.now(),
      avatar: '🌊',
      suggestions: [
        '🏥 نزدیک‌ترین بیمارستان',
        '🍽️ رستوران‌های خوب',
        '🚗 تاکسی‌های آنلاین',
        '📍 خدمات نزدیک من',
      ],
    }));

    // Notification
    dispatch(addNotification({
      title: 'خوش آمدید',
      message: 'به چت‌بات هرمزگان هوشمند خوش آمدید',
      type: 'info',
      duration: 3000,
    }));

  }, [dispatch]);

  const handleSendMessage = async (message) => {
    if (!message.trim()) return;

    // Add user message
    dispatch(addMessage({
      text: message,
      sender: 'user',
      timestamp: Date.now(),
    }));

    dispatch(setLoading(true));
    dispatch(setTyping(true));

    try {
      const response = await chatService.sendMessage(
        message,
        'user123',
        userLocation?.lat,
        userLocation?.lng,
        sessionId
      );

      await new Promise(resolve => setTimeout(resolve, 800));

      // Add bot response
      dispatch(addMessage({
        text: response.response || 'متأسفانه نتوانستم پاسخ دهم.',
        sender: 'bot',
        timestamp: Date.now(),
        avatar: '🌊',
        location: response.location,
        suggestions: response.suggestions,
        intent: response.intent,
        confidence: response.confidence,
      }));

      // Toast on success
      dispatch(addToast({
        message: 'پاسخ دریافت شد',
        type: 'success',
        duration: 2000,
      }));

    } catch (error) {
      dispatch(setError(error.message));
      
      dispatch(addMessage({
        text: '❌ خطایی رخ داد. لطفاً دوباره تلاش کنید.',
        sender: 'bot',
        timestamp: Date.now(),
        avatar: '🌊',
      }));

      dispatch(addToast({
        message: 'خطا در ارسال پیام',
        type: 'error',
        duration: 3000,
      }));

    } finally {
      dispatch(setLoading(false));
      dispatch(setTyping(false));
      dispatch(clearError());
    }
  };

  return (
    <div className={`chat-page-container ${theme === 'dark' ? 'dark' : ''}`}>
      <div className="chat-wrapper">
        <div className="chat-header-section">
          <div className="header-content">
            <h1 className="page-title">💬 چت‌بات هوشمند</h1>
            <p className="page-subtitle">پرسش‌های خود را بپرسید و پاسخ فوری دریافت کنید</p>
          </div>
        </div>

        <div className="chat-main">
          <ChatBox
            messages={messages}
            isLoading={isLoading}
            isTyping={isTyping}
            onSendMessage={handleSendMessage}
          />
        </div>
      </div>

      <div className="chat-sidebar">
        <div className="sidebar-card">
          <h3>⚡ سریع‌ترین پرسش‌ها</h3>
          <ul className="quick-list">
            <li onClick={() => handleSendMessage('نزدیک‌ترین بیمارستان کجاست؟')}>
              🏥 بیمارستان‌ها
            </li>
            <li onClick={() => handleSendMessage('رستوران‌های خوب کجاست؟')}>
              🍽️ رستوران‌ها
            </li>
            <li onClick={() => handleSendMessage('تاکسی برای من بخوان')}>
              🚗 تاکسی
            </li>
            <li onClick={() => handleSendMessage('خدمات نزدیک من')}>
              📍 خدمات نزدیک
            </li>
          </ul>
        </div>

        <div className="sidebar-card">
          <h3>ℹ️ راهنما</h3>
          <p className="info-text">می‌تونید از این دستیار برای:</p>
          <ul className="info-list">
            <li>🔍 جستجوی خدمات</li>
            <li>🗺️ مسیریابی</li>
            <li>📞 اطلاعات تماس</li>
            <li>⏰ ساعت کاری</li>
            <li>⭐ رتبه‌ها و نظرات</li>
          </ul>
        </div>

        <div className="sidebar-card stats">
          <h3>📊 آمار</h3>
          <div className="stat">
            <span className="stat-label">پرسش‌های پاسخ‌گویی شده</span>
            <span className="stat-value">۲۳۴۱</span>
          </div>
          <div className="stat">
            <span className="stat-label">رضایت کاربران</span>
            <span className="stat-value">۴.۸⭐</span>
          </div>
          <div className="stat">
            <span className="stat-label">پیام‌های امروز</span>
            <span className="stat-value">{messages.length}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;
