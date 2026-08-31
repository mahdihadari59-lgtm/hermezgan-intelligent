import { combineReducers } from '@reduxjs/toolkit';

// TODO: این‌ها بعداً باید بازسازی شوند: map, ui, hotspot, camera
import authReducer from '../features/auth/authSlice';
import chatReducer from '../features/chat/chatSlice';
import dashboardReducer from '../features/dashboard/dashboardSlice';

const rootReducer = combineReducers({
  auth: authReducer,
  chat: chatReducer,
  dashboard: dashboardReducer,
});

export default rootReducer;
