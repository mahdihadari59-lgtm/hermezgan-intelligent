import { useState, useCallback } from "react";
import { chatApi } from "@api/chat.api";
import { useAssistantStore } from "@stores/assistant.store";

export function useChat(userId = "web_user") {
  const store = useAssistantStore();

  const sendMessage = useCallback(async (message, options = {}) => {
    const userMessage = {
      id: Date.now(),
      role: "user",
      content: message,
      timestamp: new Date().toISOString(),
    };

    store.addMessage(userMessage);
    store.setIsTyping(true);

    try {
      const response = await chatApi.send(message, userId, options);

      const assistantMessage = {
        id: Date.now() + 1,
        role: "assistant",
        content: response.response || response.message || "پاسخ دریافت شد.",
        timestamp: new Date().toISOString(),
        metadata: response.metadata || {},
      };

      store.addMessage(assistantMessage);

      if (response.suggestions) {
        store.setSuggestions(response.suggestions);
      }

      return response;
    } catch (error) {
      console.error("Chat error:", error);

      const errorMessage = {
        id: Date.now() + 1,
        role: "assistant",
        content: "متأسفانه خطایی رخ داد. لطفاً دوباره تلاش کنید.",
        timestamp: new Date().toISOString(),
        isError: true,
      };

      store.addMessage(errorMessage);
      throw error;
    } finally {
      store.setIsTyping(false);
    }
  }, [store, userId]);

  const loadHistory = useCallback(async () => {
    try {
      const history = await chatApi.history(userId);
      if (Array.isArray(history)) {
        history.forEach((msg) => store.addMessage(msg));
      }
      return history;
    } catch (error) {
      console.error("History error:", error);
      return [];
    }
  }, [store, userId]);

  const clearHistory = useCallback(async () => {
    try {
      await chatApi.clear(userId);
      store.clearMessages();
    } catch (error) {
      console.error("Clear error:", error);
    }
  }, [store, userId]);

  return {
    messages: store.messages,
    isTyping: store.isTyping,
    suggestions: store.suggestions,
    sendMessage,
    loadHistory,
    clearHistory,
  };
}
