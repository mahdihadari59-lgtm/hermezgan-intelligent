import { useState, useEffect, useRef } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { addMessage, setLoading, setTyping, clearMessages } from '../store/slices/chatSlice';
import chatService from '../services/chatService';
import useLocation from './useLocation';

const useChat = (sessionId = null) => {
  const dispatch = useDispatch();
  const { messages, isLoading, isTyping, error } = useSelector(state => state.chat);
  const { location } = useLocation();
  const [currentSessionId, setCurrentSessionId] = useState(sessionId);
  const messagesEndRef = useRef(null);

  const sendMessage = async (text) => {
    if (!text || !text.trim()) return;
    dispatch(addMessage({ text, sender: 'user', timestamp: Date.now() }));
    dispatch(setLoading(true));
    dispatch(setTyping(true));
    try {
      const response = await chatService.sendMessage(text, 'user123', location?.lat, location?.lng, currentSessionId);
      if (response.session_id && !currentSessionId) setCurrentSessionId(response.session_id);
      await new Promise(resolve => setTimeout(resolve, 800 + Math.random() * 1200));
      dispatch(addMessage({ text: response.response || 'متأسفانه نتوانستم پاسخ دهم.', sender: 'bot', timestamp: Date.now(), avatar: '🌊', intent: response.intent, suggestions: response.suggestions }));
      return response;
    } catch (error) {
      dispatch(addMessage({ text: '❌ خطایی رخ داد. لطفاً دوباره تلاش کنید.', sender: 'bot', timestamp: Date.now(), avatar: '🌊' }));
      throw error;
    } finally {
      dispatch(setLoading(false));
      dispatch(setTyping(false));
    }
  };

  const clearChat = () => dispatch(clearMessages());
  const scrollToBottom = () => messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });

  useEffect(() => { scrollToBottom(); }, [messages]);

  useEffect(() => {
    if (messages.length === 0) {
      dispatch(addMessage({ text: '🌊 سلام! من دستیار هوشمند هرمزگان هستم. چگونه می‌تونم کمکتون کنم؟', sender: 'bot', timestamp: Date.now(), avatar: '🌊', suggestions: ['🏥 نزدیک‌ترین بیمارستان', '🍽️ رستوران‌های خوب', '🚗 تاکسی‌های آنلاین', '📍 خدمات نزدیک من'] }));
    }
  }, [dispatch]);

  return { messages, isLoading, isTyping, error, sessionId: currentSessionId, sendMessage, clearChat, scrollToBottom, messagesEndRef };
};

export default useChat;
