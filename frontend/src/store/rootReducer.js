import { combineReducers } from '@reduxjs/toolkit';

// Import reducers (از مسیرهای موجود)
import authReducer from '../features/auth/authSlice';
import chatReducer from '../features/chat/chatSlice';
import mapReducer from '../features/map/mapSlice';
import uiReducer from '../features/ui/uiSlice';
import dashboardReducer from '../features/dashboard/dashboardSlice';
import hotspotReducer from '../features/hotspot/hotspotSlice';
import cameraReducer from '../features/camera/cameraSlice';

const rootReducer = combineReducers({
  auth: authReducer,
  chat: chatReducer,
  map: mapReducer,
  ui: uiReducer,
  dashboard: dashboardReducer,
  hotspot: hotspotReducer,
  camera: cameraReducer,
});

export default rootReducer;
