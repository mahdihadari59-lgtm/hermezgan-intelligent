// ============================================
// راهنمای استفاده از Redux Slices
// ============================================
// ✅ نسخه‌های features کامل‌تر هستند:
//    chatSlice: 154 خط > store/slices/chatSlice (44 خط)
//    mapSlice: 64 خط > store/slices/mapSlice (34 خط)
//    uiSlice: 57 خط > store/slices/uiSlice (25 خط)
//    authSlice: 38 خط > store/slices/authSlice (33 خط)

// اسلایس‌های اصلی
export { default as authSlice } from './auth/authSlice';
export { default as chatSlice } from './chat/chatSlice';
export { default as mapSlice } from './map/mapSlice';
export { default as uiSlice } from './ui/uiSlice';

// اسلایس‌های کاربردی
export { default as cameraSlice } from './camera/cameraSlice';
export { default as dashboardSlice } from './dashboard/dashboardSlice';
export { default as hotspotSlice } from './hotspot/hotspotSlice';

// ============================================
// نحوه استفاده در پروژه:
// ============================================
// ❌ قدیمی (استفاده از store/slices):
//    import authSlice from '../store/slices/authSlice';
//
// ✅ جدید (استفاده از features):
//    import { authSlice } from '../features';
// ============================================
