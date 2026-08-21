
import api from './api';

const analyticsService = {
  getAll: async () => {
    try {
      const response = await api.get('/analytics');
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },
  getById: async (id) => {
    try {
      const response = await api.get(`/analytics/${id}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },
  create: async (data) => {
    try {
      const response = await api.post('/analytics', data);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },
  update: async (id, data) => {
    try {
      const response = await api.put(`/analytics/${id}`, data);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },
  delete: async (id) => {
    try {
      const response = await api.delete(`/analytics/${id}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },
};

export default analyticsService;
