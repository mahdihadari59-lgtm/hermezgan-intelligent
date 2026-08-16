import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  center: { lat: 27.2158, lng: 56.2808 },
  zoom: 13,
  markers: [],
  selectedMarker: null,
  searchQuery: '',
  serviceTypeFilter: null,
  mapMode: 'street',
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
    setMapMode: (state, action) => {
      state.mapMode = action.payload;
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
  setMapMode,
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
