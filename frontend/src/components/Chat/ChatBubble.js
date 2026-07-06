import React from 'react';
import './ChatBubble.css';

const ChatBubble = ({ message, isUser }) => {
  const formatTime = (timestamp) => {
    if (!timestamp) return '';

    const date = new Date(timestamp);

    if (isNaN(date.getTime())) return '';

    return date.toLocaleTimeString('fa-IR', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className={`chat-bubble-wrapper ${isUser ? 'user' : 'bot'}`}>
      {!isUser && (
        <div className="bubble-avatar">
          <span>{message?.avatar || '🌊'}</span>
        </div>
      )}

      <div className={`chat-bubble ${isUser ? 'user-message' : 'bot-message'}`}>
        <p className="bubble-text">
          {message?.text || ''}
        </p>

        {message?.location && (
          <div className="message-location">
            <span>📍 {message.location.name}</span>

            {message.location.distance && (
              <span className="distance">
                {message.location.distance} کیلومتر
              </span>
            )}
          </div>
        )}

        {Array.isArray(message?.suggestions) &&
          message.suggestions.length > 0 && (
            <div className="message-suggestions">
              {message.suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  className="suggestion-btn"
                  onClick={() =>
                    message.onSuggestionClick?.(suggestion)
                  }
                >
                  {suggestion}
                </button>
              ))}
            </div>
          )}

        <span className="bubble-time">
          {formatTime(message?.timestamp)}
        </span>
      </div>

      {isUser && (
        <div className="bubble-avatar user-avatar">
          <img
            src={
              message?.avatar ||
              'https://ui-avatars.com/api/?name=User'
            }
            alt="User"
            loading="lazy"
          />
        </div>
      )}
    </div>
  );
};

export default ChatBubble;
