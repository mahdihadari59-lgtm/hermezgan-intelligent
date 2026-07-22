import React, { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { ChatBox } from "../components/Chat";
import { addMessage, clearMessages } from "../store/slices/chatSlice";
import "./ChatPage.css";

const ChatPage = () => {
  const dispatch = useDispatch();
  const { messages, isLoading, isTyping } = useSelector((state) => state.chat);

  useEffect(() => {
    dispatch(clearMessages());
    dispatch(
      addMessage({
        text: "🌊 سلام! من دستیار هوشمند هرمزگان هستم. چگونه می‌تونم کمکتون کنم؟",
        sender: "bot",
        timestamp: Date.now(),
        avatar: "🌊",
        suggestions: [
          "🏥 نزدیک‌ترین بیمارستان",
          "🍽️ رستوران‌های خوب",
          "🚗 تاکسی‌های آنلاین",
          "📍 خدمات نزدیک من",
        ],
      })
    );
  }, [dispatch]);

  const handleSendMessage = (msg) => {
    // پیام قبلاً در MessageInput اضافه شده
  };

  return (
    <div className="chat-page">
      <div className="chat-page-container">
        <ChatBox
          messages={messages}
          isLoading={isLoading}
          isTyping={isTyping}
          onSendMessage={handleSendMessage}
        />
      </div>
    </div>
  );
};

export default ChatPage;
