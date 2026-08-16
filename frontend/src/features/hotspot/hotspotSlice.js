import { createSlice } from '@reduxjs/toolkit';

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
