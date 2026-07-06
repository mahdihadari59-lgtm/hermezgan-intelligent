import React, { useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { ChatBox } from '../components/Chat';
import { addMessage } from '../store/slices/chatSlice';
import './ChatPage.css';

const ChatPage = () => {
  const dispatch = useDispatch();

  useEffect(() => {
    dispatch(
      addMessage({
        sender: 'bot',
        text: 'سلام 👋\nبه هرمزگان هوشمند خوش آمدید.\nچطور می‌توانم کمکتان کنم؟',
        avatar: '🌊',
        suggestions: [
          '🏥 نزدیک‌ترین بیمارستان',
          '🍽️ رستوران‌های نزدیک',
          '🚕 تاکسی آنلاین',
          '🗺️ مکان‌های گردشگری'
        ]
      })
    );
  }, [dispatch]);

  return (
    <div className="chat-page">
      <div className="chat-page-container">
        <ChatBox />
      </div>
    </div>
  );
};

export default ChatPage;
