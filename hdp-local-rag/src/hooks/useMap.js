
import { useState, useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import MapService from '../services/mapService';

export const useMap = () => {
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const data = useSelector(state => state.map);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await MapService.getAll();
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
