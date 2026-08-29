import { api } from "./client";

export const chatApi = {
  send(message, userId = "web_user", options = {}) {
    return api.post("/chat/chat/message", {
      message,
      user_id: userId,
      ...options,
    });
  },

  history(userId) {
    return api.get(`/chat/chat/history/${userId}`);
  },

  clear(userId) {
    return api.delete(`/chat/chat/history/${userId}`);
  },
};
