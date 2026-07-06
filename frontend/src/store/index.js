import { configureStore } from '@reduxjs/toolkit';
import chatReducer from './slices/chatSlice';

const store = configureStore({
  reducer: {
    chat: chatReducer,
  },

  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
    }),

  devTools: process.env.NODE_ENV !== 'production',
});

export default store;
