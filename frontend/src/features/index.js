// Auto-generated barrel. Do not edit by hand.
export { default as authSlice } from './auth/authSlice';
export { default as cameraSlice } from './camera/cameraSlice';
export { default as chatSlice } from './chat/chatSlice';
export { default as dashboardSlice } from './dashboard/dashboardSlice';
export { default as hotspotSlice } from './hotspot/hotspotSlice';
export { default as mapSlice } from './map/mapSlice';
export { default as uiSlice } from './ui/uiSlice';

// Actions
export {
  clearError as clearAuthError,
  login,
  logout,
  setError as setAuthError,
  setLoading as setAuthLoading,
  setUser,
} from './auth/authSlice';

export {
  clearCameraSelection,
  clearError as clearCameraError,
  selectCamera,
  setCameraFilter,
  setCameras,
  setError as setCameraError,
  setLoading as setCameraLoading,
  setRegionFilter,
} from './camera/cameraSlice';

export {
  addMessage,
  clearError as clearChatError,
  clearMessages,
  getChatHistory,
  sendMessage,
  setError as setChatError,
  setLoading as setChatLoading,
  setSessionId,
  setTyping,
} from './chat/chatSlice';

export {
  clearError as clearDashboardError,
  setError as setDashboardError,
  setLoading as setDashboardLoading,
  setStats,
} from './dashboard/dashboardSlice';

export {
  clearError as clearHotspotError,
  clearHotspotSelection,
  selectHotspot,
  setError as setHotspotError,
  setHotspotFilter,
  setHotspots,
  setLoading as setHotspotLoading,
  toggleHotspots,
} from './hotspot/hotspotSlice';

export {
  clearError as clearMapError,
  clearSelection as clearMapSelection,
  selectMarker,
  setError as setMapError,
  setGeolocating,
  setLoading as setMapLoading,
  setMapCenter,
  setMapMode,
  setMarkers,
  setSearchQuery,
  setServiceTypeFilter,
  setUserLocation,
  setZoom,
} from './map/mapSlice';

export {
  addNotification,
  addToast,
  clearError as clearUiError,
  removeNotification,
  removeToast,
  setError as setUiError,
  setLanguage,
  setLoading as setUiLoading,
  setNotification,
  setTheme,
  toggleDarkMode,
  toggleSidebar,
} from './ui/uiSlice';
