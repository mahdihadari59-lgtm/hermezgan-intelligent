
import { useState, useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import ChatService from '../services/chatService';

export const useChat = () => {
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const data = useSelector(state => state.chat);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await ChatService.getAll();
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { data, loading, error, fetchData };
};
