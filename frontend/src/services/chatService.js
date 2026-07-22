import api from "./api";

const chatService = {
  sendMessage: async (message, userId, latitude = null, longitude = null) => {
    try {
      const response = await api.post("/chat/message", {
        message,
        user_id: userId,
        latitude,
        longitude,
      });
      return response;
    } catch (error) {
      console.error("خطا در ارسال پیام:", error);
      throw error;
    }
  },

  getChatHistory: async (userId, limit = 50) => {
    try {
      const response = await api.get(`/chat/history/${userId}`, {
        params: { limit },
      });
      return response;
    } catch (error) {
      console.error("خطا در دریافت تاریخچه:", error);
      throw error;
    }
  },

  simulateTyping: (duration = 1000) => {
    return new Promise((resolve) => setTimeout(resolve, duration));
  },
};

export default chatService;
