
import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  loading: false,
  error: null,
  data: [],
};

const hotspotSlice = createSlice({
  name: 'hotspot',
  initialState,
  reducers: {
    setLoading: (state, action) => {
      state.loading = action.payload;
    },
    setError: (state, action) => {
      state.error = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
    setHotspots: (state, action) => { state.setHotspots = action.payload; },
    selectHotspot: (state, action) => { state.selectHotspot = action.payload; }
  },
});

export const { setLoading, setError, clearError, setHotspots, selectHotspot } = hotspotSlice.actions;
export default hotspotSlice.reducer;
