import { configureStore } from '@reduxjs/toolkit';
import chatReducer from './slices/chatSlice';
import mapReducer from './slices/mapSlice';

const store = configureStore({
  reducer: {
    chat: chatReducer,
    map: mapReducer,
  },
});

export default store;
