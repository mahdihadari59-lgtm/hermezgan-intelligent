import React, { useEffect, useRef } from 'react';
import { useSelector } from 'react-redux';
import ChatBubble from './ChatBubble';
import TypingIndicator from './TypingIndicator';
import './MessageList.css';

const MessageList = () => {
  const messagesEndRef = useRef(null);

  const { messages, isTyping } = useSelector(
    (state) => state.chat
  );

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: 'smooth',
    });
  }, [messages, isTyping]);

  return (
    <div className="message-list">
      {messages.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">🌊</div>

          <h2>سلام! من هرمزگان هوشمند هستم</h2>

          <p>
            لطفاً سؤال خود را بپرسید یا یکی از گزینه‌های زیر را انتخاب کنید.
          </p>

          <div className="empty-suggestions">
            <button className="suggestion-btn">
              🏥 نزدیک‌ترین بیمارستان
            </button>

            <button className="suggestion-btn">
              🍽️ رستوران‌های نزدیک
            </button>

            <button className="suggestion-btn">
              🚗 تاکسی‌های موجود
            </button>
          </div>
        </div>
      ) : (
        <>
          {messages.map((message) => (
            <ChatBubble
              key={message.id}
              message={message}
              isUser={message.sender === 'user'}
            />
          ))}

          {isTyping && (
            <div className="typing-container">
              <div className="typing-avatar">🌊</div>
              <TypingIndicator />
            </div>
          )}

          <div ref={messagesEndRef} />
        </>
      )}
    </div>
  );
};

export default MessageList;
