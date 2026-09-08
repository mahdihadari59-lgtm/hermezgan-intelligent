
import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  loading: false,
  error: null,
  data: [],
};

const mapSlice = createSlice({
  name: 'map',
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
    setMapCenter: (state, action) => { state.setMapCenter = action.payload; },
    setZoom: (state, action) => { state.setZoom = action.payload; },
    setMarkers: (state, action) => { state.setMarkers = action.payload; }
  },
});

export const { setLoading, setError, clearError, setMapCenter, setZoom, setMarkers } = mapSlice.actions;
export default mapSlice.reducer;
