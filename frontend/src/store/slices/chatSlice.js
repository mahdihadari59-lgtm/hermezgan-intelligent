import { createSlice, nanoid } from '@reduxjs/toolkit';

const initialState = {
  messages: [],
  isLoading: false,
  isTyping: false,
  error: null,

  connectionStatus: 'online',
  unreadCount: 0,

  currentUser: {
    id: 'user123',
    name: 'شما',
    avatar: 'https://ui-avatars.com/api/?name=You&background=667eea&color=fff',
  },

  bot: {
    id: 'bot001',
    name: 'هرمزگان هوشمند',
    avatar: '🌊',
  },
};

const chatSlice = createSlice({
  name: 'chat',
  initialState,

  reducers: {
    addMessage: (state, action) => {
      state.messages.push({
        id: action.payload.id || nanoid(),
        text: action.payload.text || '',
        sender: action.payload.sender || 'user',
        type: action.payload.type || 'text',
        status: action.payload.status || 'sent',
        timestamp:
          action.payload.timestamp || new Date().toISOString(),
        avatar: action.payload.avatar || null,
        location: action.payload.location || null,
        suggestions: action.payload.suggestions || [],
        read: action.payload.read ?? false,
        ...action.payload,
      });

      if (action.payload.sender === 'bot') {
        state.unreadCount += 1;
      }
    },

    clearMessages(state) {
      state.messages = [];
      state.unreadCount = 0;
    },

    deleteMessage(state, action) {
      state.messages = state.messages.filter(
        (msg) => msg.id !== action.payload
      );
    },

    updateMessage(state, action) {
      const index = state.messages.findIndex(
        (msg) => msg.id === action.payload.id
      );

      if (index !== -1) {
        state.messages[index] = {
          ...state.messages[index],
          ...action.payload,
        };
      }
    },

    setLoading(state, action) {
      state.isLoading = action.payload;
    },

    setTyping(state, action) {
      state.isTyping = action.payload;
    },

    setError(state, action) {
      state.error = action.payload;
    },

    clearError(state) {
      state.error = null;
    },

    setConnectionStatus(state, action) {
      state.connectionStatus = action.payload;
    },

    resetUnreadCount(state) {
      state.unreadCount = 0;
    },

    markAllAsRead(state) {
      state.messages.forEach((msg) => {
        msg.read = true;
      });

      state.unreadCount = 0;
    },
  },
});

export const {
  addMessage,
  clearMessages,
 deleteMessage,
  updateMessage,
  setLoading,
  setTyping,
  setError,
  clearError,
  setConnectionStatus,
  resetUnreadCount,
  markAllAsRead,
} = chatSlice.actions;

export default chatSlice.reducer;
