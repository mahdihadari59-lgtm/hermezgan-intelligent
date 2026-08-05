import React from "react";
import "./ChatBubble.css";

const ChatBubble = ({ message, isUser }) => {
  const formatTime = (ts) => {
    if (!ts) return "";
    return new Date(ts).toLocaleTimeString("fa-IR", {
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <div className={`chat-bubble-wrapper ${isUser ? "user" : "bot"}`}>
      {!isUser && (
        <div className="bubble-avatar">
          <span>{message?.avatar || "🌊"}</span>
        </div>
      )}
      <div className={`chat-bubble ${isUser ? "user-message" : "bot-message"}`}>
        <p className="bubble-text">{message?.text || ""}</p>
        {message?.location && (
          <div className="message-location">
            <span>📍 {message.location.name}</span>
            <span className="distance">{message.location.distance} کیلومتر</span>
          </div>
        )}
        {message?.suggestions && message.suggestions.length > 0 && (
          <div className="message-suggestions">
            {message.suggestions.map((s, i) => (
              <button
                key={i}
                className="suggestion-btn"
                onClick={() => message.onSuggestionClick?.(s)}
              >
                {s}
              </button>
            ))}
          </div>
        )}
        <span className="bubble-time">{formatTime(message?.timestamp)}</span>
      </div>
      {isUser && (
        <div className="bubble-avatar user-avatar">
          <img src={message?.avatar || "👤"} alt="User" />
        </div>
      )}
    </div>
  );
};

export default ChatBubble;
