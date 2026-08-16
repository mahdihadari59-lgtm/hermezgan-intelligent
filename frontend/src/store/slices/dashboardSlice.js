import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  stats: { totalUsers: 0, activeUsers: 0, totalServices: 0, totalChats: 0, totalHotspots: 0, totalCameras: 0, activeCameras: 0 },
  timeFilter: 'weekly',
  isLoading: false,
  error: null
};

const dashboardSlice = createSlice({
  name: 'dashboard',
  initialState,
  reducers: {
    setStats: (state, action) => { state.stats = { ...state.stats, ...action.payload }; },
    setTimeFilter: (state, action) => { state.timeFilter = action.payload; },
    setLoading: (state, action) => { state.isLoading = action.payload; },
    setError: (state, action) => { state.error = action.payload; },
    clearError: (state) => { state.error = null; }
  }
});

export const { setStats, setTimeFilter, setLoading, setError, clearError } = dashboardSlice.actions;
export default dashboardSlice.reducer;
