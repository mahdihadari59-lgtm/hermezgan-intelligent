
import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  loading: false,
  error: null,
  data: [],
};

const dashboardSlice = createSlice({
  name: 'dashboard',
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
    setStats: (state, action) => { state.setStats = action.payload; },
    setUserGrowth: (state, action) => { state.setUserGrowth = action.payload; }
  },
});

export const { setLoading, setError, clearError, setStats, setUserGrowth } = dashboardSlice.actions;
export default dashboardSlice.reducer;
