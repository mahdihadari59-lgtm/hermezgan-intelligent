
import { useState, useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import AuthService from '../services/authService';

export const useAuth = () => {
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const data = useSelector(state => state.auth);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await AuthService.getAll();
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
