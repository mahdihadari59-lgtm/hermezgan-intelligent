import { create } from "zustand";

export const useAssistantStore = create((set, get) => ({
  // Chat
  messages: [],
  isTyping: false,
  suggestions: [],

  // Voice
  isListening: false,
  isSpeaking: false,
  voiceText: "",
  audioUrl: null,

  // Status
  connected: false,
  processing: false,

  // Actions
  addMessage: (message) =>
    set((state) => ({ messages: [...state.messages, message] })),

  clearMessages: () => set({ messages: [] }),

  setIsTyping: (isTyping) => set({ isTyping }),
  setSuggestions: (suggestions) => set({ suggestions }),

  setIsListening: (isListening) => set({ isListening }),
  setIsSpeaking: (isSpeaking) => set({ isSpeaking }),
  setVoiceText: (voiceText) => set({ voiceText }),
  setAudioUrl: (audioUrl) => set({ audioUrl }),

  setConnected: (connected) => set({ connected }),
  setProcessing: (processing) => set({ processing }),

  resetVoice: () =>
    set({
      isListening: false,
      isSpeaking: false,
      voiceText: "",
      audioUrl: null,
    }),
}));
