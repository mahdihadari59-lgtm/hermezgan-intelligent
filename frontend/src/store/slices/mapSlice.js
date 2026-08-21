import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  // Map Center & Zoom
  center: {
    lat: 27.2158,  // Bandar Abbas
    lng: 56.2808,
  },
  zoom: 13,

  // Markers
  markers: [],
  selectedMarker: null,

  // Search & Filter
  searchQuery: '',
  selectedServiceType: null,
  serviceTypes: [
    { id: 'hospital', name: 'بیمارستان', icon: '🏥', color: '#ff4757' },
    { id: 'restaurant', name: 'رستوران', icon: '🍽️', color: '#ffa502' },
    { id: 'taxi', name: 'تاکسی', icon: '🚗', color: '#2ed573' },
    { id: 'pharmacy', name: 'داروخانه', icon: '💊', color: '#1e90ff' },
    { id: 'school', name: 'مدرسه', icon: '🎓', color: '#9b59b6' },
  ],

  // User Location
  userLocation: null,
  isGeolocating: false,

  // Loading & Error
  isLoading: false,
  error: null,
  
  // Map State
  isMapReady: false,
  mapMode: 'default', // default, heatmap, cluster, live
  isOffline: false,
};

const mapSlice = createSlice({
  name: 'map',
  initialState,
  reducers: {
    // Set map center
    setMapCenter: (state, action) => {
      state.center = action.payload;
    },

    // Set zoom level
    setZoom: (state, action) => {
      state.zoom = action.payload;
    },

    // Set markers
    setMarkers: (state, action) => {
      state.markers = action.payload;
    },

    // Add single marker
    addMarker: (state, action) => {
      state.markers.push(action.payload);
    },

    // Select marker
    selectMarker: (state, action) => {
      state.selectedMarker = action.payload;
    },

    // Clear selection
    clearSelection: (state) => {
      state.selectedMarker = null;
    },

    // Set search query
    setSearchQuery: (state, action) => {
      state.searchQuery = action.payload;
    },

    // Set service type filter
    setServiceTypeFilter: (state, action) => {
      state.selectedServiceType = action.payload;
    },

    // Set user location
    setUserLocation: (state, action) => {
      state.userLocation = action.payload;
    },

    // Set geolocating state
    setGeolocating: (state, action) => {
      state.isGeolocating = action.payload;
    },

    // Set loading
    setLoading: (state, action) => {
      state.isLoading = action.payload;
    },

    // Set error
    setError: (state, action) => {
      state.error = action.payload;
    },

    // Clear error
    clearError: (state) => {
      state.error = null;
    },

    // Map ready
    setMapReady: (state, action) => {
      state.isMapReady = action.payload;
    },

    // Set map mode
    setMapMode: (state, action) => {
      state.mapMode = action.payload;
    },

    // Toggle offline
    toggleOffline: (state) => {
      state.isOffline = !state.isOffline;
    },
  },
});

export const {
  setMapCenter,
  setZoom,
  setMarkers,
  addMarker,
  selectMarker,
  clearSelection,
  setSearchQuery,
  setServiceTypeFilter,
  setUserLocation,
  setGeolocating,
  setLoading,
  setError,
  clearError,
  setMapReady,
  setMapMode,
  toggleOffline,
} = mapSlice.actions;

export default mapSlice.reducer;
