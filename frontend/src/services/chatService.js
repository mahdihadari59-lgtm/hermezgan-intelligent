import { chatApi } from '../api/chat.api';

const chatService = {
  sendMessage: async (
    message,
    userId = 'web_user',
    latitude = null,
    longitude = null,
    sessionId = null
  ) => {
    try {
      return await chatApi.send(message, userId, {
        latitude,
        longitude,
        ...(sessionId ? { session_id: sessionId } : {}),
      });
    } catch (error) {
      throw error;
    }
  },

  getChatHistory: async (userId) => {
    try {
      return await chatApi.history(userId);
    } catch (error) {
      throw error;
    }
  },

  deleteMessage: async (messageId) => {
    throw new Error(
      `deleteMessage(${messageId}) is not implemented by the current chat API`
    );
  },

  simulateTyping: (duration = 1000) => {
    return new Promise(resolve => setTimeout(resolve, duration));
  },
};

export default chatService;
