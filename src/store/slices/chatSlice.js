
import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  loading: false,
  error: null,
  data: [],
};

const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    setLoading: (state, action) => {
      state.loading = action.payload;
    },
    setError: (state, action) => {
      state.error = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
    addMessage: (state, action) => { state.addMessage = action.payload; },
    setTyping: (state, action) => { state.setTyping = action.payload; },
    clearMessages: (state, action) => { state.clearMessages = action.payload; }
  },
});

export const { setLoading, setError, clearError, addMessage, setTyping, clearMessages } = chatSlice.actions;
export default chatSlice.reducer;
