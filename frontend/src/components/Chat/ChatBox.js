import React, { useEffect, useRef } from "react";
import { useSelector } from "react-redux";
import MessageList from "./MessageList";
import MessageInput from "./MessageInput";
import "./ChatBox.css";

const ChatBox = ({ messages, isLoading, isTyping, onSendMessage }) => {
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  return (
    <div className="chat-box-container">
      <div className="chat-box-header">
        <div className="header-left">
          <h2 className="chat-title">🌊 هرمزگان هوشمند</h2>
          <div className="status-indicator">
            <span className="status-dot"></span>
            <span className="status-text">آنلاین</span>
          </div>
        </div>
        <div className="header-actions">
          <button className="header-btn" title="تنظیمات">
            ⚙️
          </button>
          <button className="header-btn" title="صدای روشن/خاموش">
            🔊
          </button>
          <button className="header-btn" title="بیشتر">
            ⋯
          </button>
        </div>
      </div>
      <MessageList messages={messages} isTyping={isTyping} isLoading={isLoading} />
      <MessageInput onSendMessage={onSendMessage} />
      {isLoading && (
        <div className="loading-overlay">
          <div className="loading-spinner"></div>
        </div>
      )}
    </div>
  );
};

export default ChatBox;
