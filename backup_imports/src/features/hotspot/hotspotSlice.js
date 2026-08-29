import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  hotspots: [],
  selectedHotspot: null,
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

export const { setHotspots, selectHotspot, clearSelection, setLoading, setError, clearError } = hotspotSlice.actions;
export default hotspotSlice.reducer;
