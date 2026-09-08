
import { useState, useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import LocalStorageService from '../services/localstorageService';

export const useLocalStorage = () => {
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const data = useSelector(state => state.localstorage);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await LocalStorageService.getAll();
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
