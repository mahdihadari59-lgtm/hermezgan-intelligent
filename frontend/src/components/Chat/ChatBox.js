import React from 'react';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import './ChatBox.css';

const ChatBox = () => {
  return (
    <div className="chat-box">
      <header className="chat-header">
        <div className="chat-header-info">
          <h2 className="chat-title">
            🌊 هرمزگان هوشمند
          </h2>

          <p className="chat-status">
            🟢 آنلاین
          </p>
        </div>

        <div className="chat-header-actions">
          <button
            type="button"
            className="header-action-btn"
            title="تنظیمات"
            aria-label="تنظیمات"
          >
            ⚙️
          </button>

          <button
            type="button"
            className="header-action-btn"
            title="بیشتر"
            aria-label="منوی بیشتر"
          >
            ⋮
          </button>
        </div>
      </header>

      <main className="chat-content">
        <MessageList />
      </main>

      <footer className="chat-footer">
        <MessageInput />
      </footer>
    </div>
  );
};

export default ChatBox;
