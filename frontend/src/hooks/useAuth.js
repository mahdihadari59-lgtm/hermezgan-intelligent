import { useSelector, useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import authService from '../services/authService';

const useAuth = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { user, isAuthenticated, loading, error } = useSelector(state => state.auth);

  const login = async (username, password) => {
    try {
      const response = await authService.login(username, password);
      localStorage.setItem('token', response.token);
      navigate('/dashboard');
      return true;
    } catch (error) {
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  return { user, isAuthenticated, loading, error, login, logout };
};

export default useAuth;
