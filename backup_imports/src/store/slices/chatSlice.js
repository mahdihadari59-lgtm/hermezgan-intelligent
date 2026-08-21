import { createSlice } from "@reduxjs/toolkit";

const initialState = {
  messages: [],
  isLoading: false,
  isTyping: false,
  error: null,
  currentUser: {
    id: "user123",
    name: "شما",
    avatar: "https://ui-avatars.com/api/?name=You&background=667eea&color=fff",
  },
  bot: {
    id: "bot001",
    name: "هرمزگان هوشمند",
    avatar: "🌊",
  },
};

const chatSlice = createSlice({
  name: "chat",
  initialState,
  reducers: {
    addMessage: (state, action) => {
      state.messages.push({ id: Date.now(), ...action.payload });
    },
    clearMessages: (state) => {
      state.messages = [];
    },
    setLoading: (state, action) => {
      state.isLoading = action.payload;
    },
    setTyping: (state, action) => {
      state.isTyping = action.payload;
    },
    setError: (state, action) => {
      state.error = action.payload;
    },
  },
});

export const { addMessage, clearMessages, setLoading, setTyping, setError } =
  chatSlice.actions;
export default chatSlice.reducer;
