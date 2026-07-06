import api from './api';

const handleError = (error) => {
  if (error.response) {
    throw {
      success: false,
      status: error.response.status,
      message:
        error.response.data?.message ||
        error.response.data?.error ||
        'Server Error',
      data: error.response.data,
    };
  }

  if (error.request) {
    throw {
      success: false,
      status: 0,
      message: 'Cannot connect to server',
    };
  }

  throw {
    success: false,
    status: -1,
    message: error.message || 'Unknown error',
  };
};

const chatService = {
  // ارسال پیام
  async sendMessage(message, userId, latitude = null, longitude = null) {
    try {
      const { data } = await api.post('/chat/message', {
        message,
        user_id: userId,
        latitude,
        longitude,
      });

      return data;
    } catch (error) {
      handleError(error);
    }
  },

  // دریافت تاریخچه گفتگو
  async getChatHistory(userId, limit = 50) {
    try {
      const { data } = await api.get('/chat/history', {
        params: {
          user_id: userId,
          limit,
        },
      });

      return data;
    } catch (error) {
      handleError(error);
    }
  },

  // حذف یک پیام
  async deleteMessage(messageId) {
    try {
      const { data } = await api.delete(`/chat/message/${messageId}`);
      return data;
    } catch (error) {
      handleError(error);
    }
  },

  // حذف کل تاریخچه
  async clearHistory(userId) {
    try {
      const { data } = await api.delete('/chat/history', {
        data: {
          user_id: userId,
        },
      });

      return data;
    } catch (error) {
      handleError(error);
    }
  },

  // بررسی سلامت API
  async healthCheck() {
    try {
      const { data } = await api.get('/health');
      return data;
    } catch (error) {
      handleError(error);
    }
  },

  // شبیه‌سازی تایپ ربات
  simulateTyping(duration = 1000) {
    return new Promise((resolve) => {
      setTimeout(resolve, duration);
    });
  },
};

export default chatService;
