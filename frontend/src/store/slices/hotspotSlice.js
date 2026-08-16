import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  hotspots: [],
  selectedHotspot: null,
  showHotspots: true,
  hotspotFilter: 'all',
  hotspotTypes: [
    { id: 'accident', name: 'تصادف', icon: '🚗💥', color: '#ff4757' },
    { id: 'traffic', name: 'ترافیک', icon: '🚦🚗', color: '#ffa502' },
    { id: 'danger', name: 'مناطق خطرناک', icon: '⚠️', color: '#ff6348' },
    { id: 'construction', name: 'ساخت و ساز', icon: '🏗️', color: '#ffd700' },
  ],
  isLoading: false,
  error: null,
};

const hotspotSlice = createSlice({
  name: 'hotspot',
  initialState,
  reducers: {
    setHotspots: (state, action) => { state.hotspots = action.payload; },
    addHotspot: (state, action) => { state.hotspots.push({ id: Date.now(), ...action.payload }); },
    selectHotspot: (state, action) => { state.selectedHotspot = action.payload; },
    clearHotspotSelection: (state) => { state.selectedHotspot = null; },
    toggleHotspots: (state) => { state.showHotspots = !state.showHotspots; },
    setHotspotFilter: (state, action) => { state.hotspotFilter = action.payload; },
    deleteHotspot: (state, action) => {
      state.hotspots = state.hotspots.filter(h => h.id !== action.payload);
      if (state.selectedHotspot?.id === action.payload) state.selectedHotspot = null;
    },
    updateHotspot: (state, action) => {
      const index = state.hotspots.findIndex(h => h.id === action.payload.id);
      if (index !== -1) state.hotspots[index] = { ...state.hotspots[index], ...action.payload };
    },
    setLoading: (state, action) => { state.isLoading = action.payload; },
    setError: (state, action) => { state.error = action.payload; },
    clearError: (state) => { state.error = null; },
  },
});

export const {
  setHotspots,
  addHotspot,
  selectHotspot,
  clearHotspotSelection,
  toggleHotspots,
  setHotspotFilter,
  deleteHotspot,
  updateHotspot,
  setLoading,
  setError,
  clearError,
} = hotspotSlice.actions;

export default hotspotSlice.reducer;
