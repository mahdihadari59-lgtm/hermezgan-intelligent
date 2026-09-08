
import { useState, useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import CameraService from '../services/cameraService';

export const useCamera = () => {
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const data = useSelector(state => state.camera);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await CameraService.getAll();
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
