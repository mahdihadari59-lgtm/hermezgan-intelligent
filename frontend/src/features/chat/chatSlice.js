import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api';

// ============================================================
// Async Thunks
// ============================================================

// ارسال پیام به سرور
export const sendMessage = createAsyncThunk(
  'chat/sendMessage',
  async ({ message, user_id, latitude, longitude }, { rejectWithValue }) => {
    try {
      const response = await api.post('/chat/message', {
        message,
        user_id,
        latitude,
        longitude
      });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || error.message);
    }
  }
);

// دریافت تاریخچه چت
export const getChatHistory = createAsyncThunk(
  'chat/getHistory',
  async ({ user_id, limit = 50 }, { rejectWithValue }) => {
    try {
      const response = await api.get(`/chat/history/${user_id}`, {
        params: { limit }
      });
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || error.message);
    }
  }
);

// ============================================================
// Initial State
// ============================================================
const initialState = {
  messages: [],
  isLoading: false,
  isTyping: false,
  error: null,
  sessionId: null,
  totalMessages: 0,
};

// ============================================================
// Slice
// ============================================================
const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    // اضافه کردن پیام جدید
    addMessage: (state, action) => {
      state.messages.push({
        id: Date.now(),
        ...action.payload,
      });
      state.totalMessages += 1;
    },
    // پاک کردن همه پیام‌ها
    clearMessages: (state) => {
      state.messages = [];
      state.totalMessages = 0;
    },
    // تنظیم وضعیت تایپ کردن
    setTyping: (state, action) => {
      state.isTyping = action.payload;
    },
    // تنظیم وضعیت بارگذاری
    setLoading: (state, action) => {
      state.isLoading = action.payload;
    },
    // تنظیم Session ID
    setSessionId: (state, action) => {
      state.sessionId = action.payload;
    },
    // تنظیم خطا
    setError: (state, action) => {
      state.error = action.payload;
    },
    // پاک کردن خطا
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // ===== Send Message =====
      .addCase(sendMessage.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(sendMessage.fulfilled, (state, action) => {
        state.isLoading = false;
        state.isTyping = false;
        if (action.payload?.session_id) {
          state.sessionId = action.payload.session_id;
        }
        // اگر پیام پاسخ در payload وجود داشت، اضافه کن
        if (action.payload?.response) {
          state.messages.push({
            id: Date.now() + 1,
            text: action.payload.response,
            sender: 'bot',
            timestamp: new Date().toISOString(),
            avatar: '🌊',
            intent: action.payload?.intent,
            suggestions: action.payload?.suggestions
          });
        }
      })
      .addCase(sendMessage.rejected, (state, action) => {
        state.isLoading = false;
        state.isTyping = false;
        state.error = action.payload || 'خطا در ارسال پیام';
      })
      // ===== Get History =====
      .addCase(getChatHistory.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(getChatHistory.fulfilled, (state, action) => {
        state.isLoading = false;
        state.messages = action.payload?.messages || [];
        state.totalMessages = action.payload?.total || 0;
      })
      .addCase(getChatHistory.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload || 'خطا در دریافت تاریخچه';
      });
  },
});

// ============================================================
// Exports
// ============================================================
export const {
  addMessage,
  clearMessages,
  setTyping,
  setLoading,
  setSessionId,
  setError,
  clearError,
} = chatSlice.actions;

export default chatSlice.reducer;
