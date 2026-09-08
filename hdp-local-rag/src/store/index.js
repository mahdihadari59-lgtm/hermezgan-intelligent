import { configureStore } from '@reduxjs/toolkit';
import uiReducer from './slices/uiSlice';
import authReducer from './slices/authSlice';
import chatReducer from './slices/chatSlice';
import mapReducer from './slices/mapSlice';
import hotspotReducer from './slices/hotspotSlice';
import cameraReducer from './slices/cameraSlice';
import dashboardReducer from './slices/dashboardSlice';

const store = configureStore({
  reducer: {
    ui: uiReducer,
    auth: authReducer,
    chat: chatReducer,
    map: mapReducer,
    hotspot: hotspotReducer,
    camera: cameraReducer,
    dashboard: dashboardReducer,
  },
  devTools: process.env.NODE_ENV !== 'production',
});

export default store;
