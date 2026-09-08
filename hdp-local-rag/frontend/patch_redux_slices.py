#!/usr/bin/env python3
# ============================================================
# patch_redux_slices.py
# اضافه‌کردن اکشن‌های گم‌شده به Redux slices
# ============================================================
import os

BASE = "src/features"

# ---------- uiSlice: setTheme, setNotification ----------
ui_path = os.path.join(BASE, "ui", "uiSlice.js")
ui_new = """import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  isSidebarOpen: true,
  isDarkMode: false,
  theme: 'light',
  language: 'fa',
  notifications: [],
  loading: false,
  error: null,
};

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    toggleSidebar: (state) => {
      state.isSidebarOpen = !state.isSidebarOpen;
    },
    toggleDarkMode: (state) => {
      state.isDarkMode = !state.isDarkMode;
      state.theme = state.isDarkMode ? 'dark' : 'light';
    },
    setTheme: (state, action) => {
      state.theme = action.payload;
      state.isDarkMode = action.payload === 'dark';
    },
    setLanguage: (state, action) => {
      state.language = action.payload;
    },
    addNotification: (state, action) => {
      state.notifications.push({
        id: Date.now(),
        ...action.payload,
      });
    },
    setNotification: (state, action) => {
      state.notifications.push({
        id: Date.now(),
        ...action.payload,
      });
    },
    removeNotification: (state, action) => {
      state.notifications = state.notifications.filter(n => n.id !== action.payload);
    },
    setLoading: (state, action) => {
      state.loading = action.payload;
    },
    setError: (state, action) => {
      state.error = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
});

export const {
  toggleSidebar,
  toggleDarkMode,
  setTheme,
  setLanguage,
  addNotification,
  setNotification,
  removeNotification,
  setLoading,
  setError,
  clearError,
} = uiSlice.actions;

export default uiSlice.reducer;
"""

# ---------- mapSlice: setGeolocating, setServiceTypeFilter ----------
map_path = os.path.join(BASE, "map", "mapSlice.js")
map_new = """import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  center: { lat: 27.2158, lng: 56.2808 },
  zoom: 13,
  markers: [],
  selectedMarker: null,
  searchQuery: '',
  serviceTypeFilter: null,
  userLocation: null,
  isGeolocating: false,
  isLoading: false,
  error: null,
};

const mapSlice = createSlice({
  name: 'map',
  initialState,
  reducers: {
    setMapCenter: (state, action) => {
      state.center = action.payload;
    },
    setZoom: (state, action) => {
      state.zoom = action.payload;
    },
    setMarkers: (state, action) => {
      state.markers = action.payload;
    },
    selectMarker: (state, action) => {
      state.selectedMarker = action.payload;
    },
    clearSelection: (state) => {
      state.selectedMarker = null;
    },
    setSearchQuery: (state, action) => {
      state.searchQuery = action.payload;
    },
    setServiceTypeFilter: (state, action) => {
      state.serviceTypeFilter = action.payload;
    },
    setUserLocation: (state, action) => {
      state.userLocation = action.payload;
    },
    setGeolocating: (state, action) => {
      state.isGeolocating = action.payload;
    },
    setLoading: (state, action) => {
      state.isLoading = action.payload;
    },
    setError: (state, action) => {
      state.error = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
});

export const {
  setMapCenter,
  setZoom,
  setMarkers,
  selectMarker,
  clearSelection,
  setSearchQuery,
  setServiceTypeFilter,
  setUserLocation,
  setGeolocating,
  setLoading,
  setError,
  clearError,
} = mapSlice.actions;

export default mapSlice.reducer;
"""

# ---------- cameraSlice: setCameraFilter, setRegionFilter, clearCameraSelection ----------
camera_path = os.path.join(BASE, "camera", "cameraSlice.js")
camera_new = """import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  cameras: [],
  selectedCamera: null,
  cameraFilter: null,
  regionFilter: null,
  isLoading: false,
  error: null,
};

const cameraSlice = createSlice({
  name: 'camera',
  initialState,
  reducers: {
    setCameras: (state, action) => {
      state.cameras = action.payload;
    },
    selectCamera: (state, action) => {
      state.selectedCamera = action.payload;
    },
    clearSelection: (state) => {
      state.selectedCamera = null;
    },
    clearCameraSelection: (state) => {
      state.selectedCamera = null;
    },
    setCameraFilter: (state, action) => {
      state.cameraFilter = action.payload;
    },
    setRegionFilter: (state, action) => {
      state.regionFilter = action.payload;
    },
    setLoading: (state, action) => {
      state.isLoading = action.payload;
    },
    setError: (state, action) => {
      state.error = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
});

export const {
  setCameras,
  selectCamera,
  clearSelection,
  clearCameraSelection,
  setCameraFilter,
  setRegionFilter,
  setLoading,
  setError,
  clearError,
} = cameraSlice.actions;

export default cameraSlice.reducer;
"""

# ---------- hotspotSlice: setHotspotFilter, clearHotspotSelection, toggleHotspots ----------
hotspot_path = os.path.join(BASE, "hotspot", "hotspotSlice.js")
hotspot_new = """import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  hotspots: [],
  selectedHotspot: null,
  hotspotFilter: null,
  showHotspots: true,
  isLoading: false,
  error: null,
};

const hotspotSlice = createSlice({
  name: 'hotspot',
  initialState,
  reducers: {
    setHotspots: (state, action) => {
      state.hotspots = action.payload;
    },
    selectHotspot: (state, action) => {
      state.selectedHotspot = action.payload;
    },
    clearSelection: (state) => {
      state.selectedHotspot = null;
    },
    clearHotspotSelection: (state) => {
      state.selectedHotspot = null;
    },
    setHotspotFilter: (state, action) => {
      state.hotspotFilter = action.payload;
    },
    toggleHotspots: (state) => {
      state.showHotspots = !state.showHotspots;
    },
    setLoading: (state, action) => {
      state.isLoading = action.payload;
    },
    setError: (state, action) => {
      state.error = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
});

export const {
  setHotspots,
  selectHotspot,
  clearSelection,
  clearHotspotSelection,
  setHotspotFilter,
  toggleHotspots,
  setLoading,
  setError,
  clearError,
} = hotspotSlice.actions;

export default hotspotSlice.reducer;
"""

# ---------- authSlice: login (async thunk) ----------
auth_path = os.path.join(BASE, "auth", "authSlice.js")
auth_new = """import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

export const login = createAsyncThunk(
  'auth/login',
  async (credentials, { rejectWithValue }) => {
    try {
      const response = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials),
      });
      if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        return rejectWithValue(err.detail || 'ورود ناموفق بود');
      }
      const data = await response.json();
      if (data.token) {
        localStorage.setItem('token', data.token);
      }
      return data;
    } catch (e) {
      return rejectWithValue(e.message || 'خطای شبکه');
    }
  }
);

const initialState = {
  user: null,
  token: localStorage.getItem('token'),
  isAuthenticated: false,
  isLoading: false,
  error: null,
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setUser: (state, action) => {
      state.user = action.payload;
      state.isAuthenticated = true;
    },
    logout: (state) => {
      state.user = null;
      state.token = null;
      state.isAuthenticated = false;
      localStorage.removeItem('token');
    },
    setLoading: (state, action) => {
      state.isLoading = action.payload;
    },
    setError: (state, action) => {
      state.error = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(login.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.isLoading = false;
        state.user = action.payload.user || action.payload;
        state.token = action.payload.token || state.token;
        state.isAuthenticated = true;
      })
      .addCase(login.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload || 'ورود ناموفق بود';
      });
  },
});

export const { setUser, logout, setLoading, setError, clearError } = authSlice.actions;
export default authSlice.reducer;
"""

# ---------- helpers.js: formatDistance ----------
helpers_path = "src/utils/helpers.js"
helpers_addition = """
export const formatDistance = (km) => {
  if (km == null || isNaN(km)) return '';
  if (km < 1) return `${Math.round(km * 1000)} متر`;
  return `${km.toFixed(1)} کیلومتر`;
};
"""

files_to_write = [
    (ui_path, ui_new),
    (map_path, map_new),
    (camera_path, camera_new),
    (hotspot_path, hotspot_new),
    (auth_path, auth_new),
]

for path, content in files_to_write:
    if not os.path.exists(path):
        print(f"⚠️ فایل پیدا نشد: {path} — رد شد")
        continue
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ بازنویسی شد: {path}")

# append formatDistance to helpers.js (avoid duplicate)
if os.path.exists(helpers_path):
    with open(helpers_path, "r", encoding="utf-8") as f:
        existing = f.read()
    if "formatDistance" not in existing:
        with open(helpers_path, "a", encoding="utf-8") as f:
            f.write(helpers_addition)
        print(f"✅ اضافه شد: {helpers_path} (formatDistance)")
    else:
        print(f"⚠️ formatDistance از قبل در {helpers_path} وجود دارد")
else:
    print(f"⚠️ فایل پیدا نشد: {helpers_path}")

print("\n🎉 پچ کامل شد.")
