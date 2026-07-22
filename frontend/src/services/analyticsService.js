import api from './api';

const analyticsService = {
  getStats: async (dateRange = 'month') => {
    try {
      const response = await api.get('/analytics/stats', { params: { range: dateRange } });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },
  getMockStats: () => {
    return { totalUsers: 1234, activeUsers: 567, totalServices: 89, totalChats: 4567, averageRating: 4.6 };
  },
};

export default analyticsService;
