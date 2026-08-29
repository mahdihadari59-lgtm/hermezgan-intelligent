import React, { useState } from "react";
import { useSelector, useDispatch } from "react-redux";
import { addMessage, setTyping, setLoading } from "../../store/slices/chatSlice";
import chatService from "../../services/chatService";
import "./MessageInput.css";

const MessageInput = ({ onSendMessage }) => {
  const dispatch = useDispatch();
  const { currentUser } = useSelector((state) => state.chat);
  const { userLocation } = useSelector((state) => state.map);
  const [message, setMessage] = useState("");
  const [isRecording, setIsRecording] = useState(false);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!message.trim()) return;

    const msg = message;
    setMessage("");

    dispatch(
      addMessage({
        text: msg,
        sender: "user",
        timestamp: Date.now(),
        avatar: currentUser?.avatar || "👤",
      })
    );

    dispatch(setLoading(true));
    dispatch(setTyping(true));

    try {
      const response = await chatService.sendMessage(
        msg,
        currentUser?.id || "user123",
        userLocation?.lat,
        userLocation?.lng
      );

      await new Promise((resolve) => setTimeout(resolve, 1000));

      dispatch(
        addMessage({
          text: response?.response || "پاسخ دریافت شد!",
          sender: "bot",
          timestamp: Date.now(),
          avatar: "🌊",
          suggestions: response?.suggestions || [],
        })
      );
    } catch (error) {
      dispatch(
        addMessage({
          text: "❌ خطایی رخ داد. لطفاً دوباره تلاش کنید.",
          sender: "bot",
          timestamp: Date.now(),
          avatar: "🌊",
        })
      );
    } finally {
      dispatch(setLoading(false));
      dispatch(setTyping(false));
    }
  };

  return (
    <form className="message-input-form" onSubmit={handleSend}>
      <div className="input-wrapper">
        <button
          type="button"
          className={`input-btn voice-btn ${isRecording ? "recording" : ""}`}
          onClick={() => setIsRecording(!isRecording)}
          title={isRecording ? "توقف ضبط" : "ضبط صدا"}
        >
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
            {isRecording ? (
              <rect x="8" y="4" width="3" height="16" />
            ) : (
              <path d="M12 1a3 3 0 00-3 3v8a3 3 0 006 0V4a3 3 0 00-3-3z" />
            )}
          </svg>
        </button>
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="پیام خود را بنویسید..."
          className="message-input"
          disabled={isRecording}
        />
        <button
          type="submit"
          className="input-btn send-btn"
          disabled={!message.trim() || isRecording}
        >
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M16.6915026,12.4744748 L3.50612381,13.2599618 C3.19218622,13.2599618 3.03521743,13.4170592 3.03521743,13.5741566 L1.15159189,20.0151496 C0.8376543,20.8006365 0.99,21.89 1.77946707,22.52 C2.41,22.99 3.50612381,23.1 4.13399899,22.8429026 L21.714504,14.0454487 C22.6563168,13.5741566 23.1272231,12.6315722 22.9702544,11.6889879 L4.13399899,1.16émis02545 C3.34915502,0.9029571 2.40734225,1.00636533 1.77946707,1.4776575 C0.994623095,2.10604706 0.837654326,3.0486314 1.15159189,3.99701575 L3.03521743,10.4380088 C3.03521743,10.5951061 3.34915502,10.7521035 3.50612381,10.7521035 L16.6915026,11.5375905 C16.6915026,11.5375905 17.1624089,11.5375905 17.1624089,12.0088827 C17.1624089,12.4744748 16.6915026,12.4744748 16.6915026,12.4744748 Z" />
          </svg>
        </button>
      </div>
    </form>
  );
};

export default MessageInput;
