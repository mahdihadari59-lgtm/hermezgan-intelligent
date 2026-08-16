// ============================================
// راهنمای استفاده از Redux Store
// ============================================
// ⚠️  توجه: نسخه‌های کامل‌تر در features/ هستند
//    برای import از features استفاده کنید:
//    import { authSlice, chatSlice } from '../features';

// تنظیمات store
import { configureStore } from '@reduxjs/toolkit';
import {
  authSlice,
  chatSlice,
  mapSlice,
  uiSlice,
  cameraSlice,
  dashboardSlice,
  hotspotSlice
} from '../features';

export const store = configureStore({
  reducer: {
    auth: authSlice,
    chat: chatSlice,
    map: mapSlice,
    ui: uiSlice,
    camera: cameraSlice,
    dashboard: dashboardSlice,
    hotspot: hotspotSlice,
  },
});

export default store;
