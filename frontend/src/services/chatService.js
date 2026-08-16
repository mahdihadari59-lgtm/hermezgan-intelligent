import api from './api';

const chatService = {
  // Send message to backend
  sendMessage: async (message, userId, latitude = null, longitude = null) => {
    try {
      const response = await api.post('/chat/message', {
        message,
        user_id: userId,
        latitude,
        longitude,
      });
      return response;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Get chat history
  getChatHistory: async (userId, limit = 50) => {
    try {
      const response = await api.get(`/chat/history/${userId}`, {
        params: { limit },
      });
      return response;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Simulate typing
  simulateTyping: (duration = 1000) => {
    return new Promise(resolve => setTimeout(resolve, duration));
  },
};

export default chatService;
