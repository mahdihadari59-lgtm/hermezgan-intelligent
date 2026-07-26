import React, { useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { ChatBox } from '../components/Chat';
import { addMessage, clearMessages } from '../store/slices/chatSlice';
import './ChatPage.css';

const ChatPage = () => {
  const dispatch = useDispatch();

  useEffect(() => {
    dispatch(clearMessages());
    dispatch(addMessage({
      text: '🌊 سلام! من دستیار هوشمند هرمزگان هستم. چگونه می‌تونم کمکتون کنم؟',
      sender: 'bot',
      timestamp: Date.now(),
      avatar: '🌊',
      suggestions: ['🏥 نزدیک‌ترین بیمارستان', '🍽️ رستوران‌های خوب', '🚗 تاکسی‌های آنلاین', '📍 خدمات نزدیک من'],
    }));
  }, [dispatch]);

  const handleSendMessage = (msg) => {
    dispatch(addMessage({ text: msg, sender: 'user', timestamp: Date.now() }));
    setTimeout(() => {
      dispatch(addMessage({
        text: 'پاسخ شما دریافت شد! ما در حال پردازش هستیم...',
        sender: 'bot',
        timestamp: Date.now(),
        avatar: '🌊',
      }));
    }, 1000);
  };

  return (
    <div className="chat-page">
      <div className="chat-page-container">
        <ChatBox messages={[]} isLoading={false} isTyping={false} onSendMessage={handleSendMessage} />
      </div>
    </div>
  );
};

export default ChatPage;
