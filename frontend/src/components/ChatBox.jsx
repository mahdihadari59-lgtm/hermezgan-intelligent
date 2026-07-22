import React, { useState, useRef, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { sendMessage, addMessage, setTyping, clearMessages } from '../features/chat/chatSlice';
import './ChatBox.css';

const ChatBox = () => {
  const dispatch = useDispatch();
  const { messages, isTyping, isLoading } = useSelector((state) => state.chat);
  const { user } = useSelector((state) => state.auth);
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    const text = inputValue.trim();
    if (!text) return;

    // Add user message
    dispatch(addMessage({
      text: text,
      sender: 'user',
      timestamp: new Date().toISOString(),
      avatar: user?.avatar || '👤'
    }));

    setInputValue('');
    dispatch(setTyping(true));

    try {
      const response = await dispatch(sendMessage({
        message: text,
        user_id: user?.id || 'guest',
        latitude: user?.latitude || null,
        longitude: user?.longitude || null
      })).unwrap();

      // Bot response is added in the slice
      if (!response?.response) {
        dispatch(addMessage({
          text: '✅ پیام شما دریافت شد!',
          sender: 'bot',
          timestamp: new Date().toISOString(),
          avatar: '🌊'
        }));
      }
    } catch (error) {
      dispatch(addMessage({
        text: '❌ خطا در ارسال پیام. لطفاً دوباره تلاش کنید.',
        sender: 'bot',
        timestamp: new Date().toISOString(),
        avatar: '🌊'
      }));
    } finally {
      dispatch(setTyping(false));
    }
  };

  const handleClearChat = () => {
    if (window.confirm('آیا از پاک کردن تمام پیام‌ها اطمینان دارید؟')) {
      dispatch(clearMessages());
    }
  };

  return (
    <div className="chat-box-wrapper">
      {/* Header */}
      <div className="chat-header">
        <div className="chat-header-left">
          <h2 className="chat-title">🌊 هرمزگان هوشمند</h2>
          <span className="chat-status">🟢 آنلاین</span>
          <span className="chat-messages-count">{messages.length} پیام</span>
        </div>
        <div className="chat-header-right">
          <button 
            className="header-btn" 
            title="پاک کردن چت"
            onClick={handleClearChat}
          >
            🗑️
          </button>
          <button className="header-btn" title="تنظیمات">⚙️</button>
          <button className="header-btn" title="بیشتر">⋯</button>
        </div>
      </div>

      {/* Messages */}
      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🌊</div>
            <h3>به هرمزگان هوشمند خوش آمدید!</h3>
            <p>سوال خود را بپرسید تا به شما کمک کنم.</p>
            <div className="quick-suggestions">
              <button onClick={() => setInputValue('نزدیک‌ترین بیمارستان کجاست؟')}>
                🏥 بیمارستان
              </button>
              <button onClick={() => setInputValue('رستوران خوب معرفی کن')}>
                🍽️ رستوران
              </button>
              <button onClick={() => setInputValue('تاکسی برای من بخوان')}>
                🚗 تاکسی
              </button>
            </div>
          </div>
        ) : (
          messages.map((msg, index) => (
            <div 
              key={msg.id || index} 
              className={`message ${msg.sender === 'user' ? 'user-message' : 'bot-message'}`}
            >
              <div className="message-avatar">
                {msg.sender === 'user' ? '👤' : '🌊'}
              </div>
              <div className="message-content">
                <div className="message-bubble">
                  <p>{msg.text}</p>
                  {msg.suggestions && msg.suggestions.length > 0 && (
                    <div className="message-suggestions">
                      {msg.suggestions.map((suggestion, i) => (
                        <button 
                          key={i} 
                          className="suggestion-btn"
                          onClick={() => setInputValue(suggestion)}
                        >
                          {suggestion}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
                <span className="message-time">
                  {new Date(msg.timestamp).toLocaleTimeString('fa-IR')}
                </span>
              </div>
            </div>
          ))
        )}
        
        {isTyping && (
          <div className="typing-indicator">
            <span className="typing-dot"></span>
            <span className="typing-dot"></span>
            <span className="typing-dot"></span>
            <span className="typing-text">در حال تایپ...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form className="chat-input-form" onSubmit={handleSendMessage}>
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="پیام خود را بنویسید..."
          className="chat-input"
          disabled={isLoading}
        />
        <button 
          type="submit" 
          className="chat-send-btn"
          disabled={isLoading || !inputValue.trim()}
        >
          {isLoading ? '⏳' : '📤'}
        </button>
      </form>
    </div>
  );
};

export default ChatBox;
