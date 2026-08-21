
import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  loading: false,
  error: null,
  data: [],
};

const authSlice = createSlice({
  name: 'auth',
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
    login: (state, action) => { state.login = action.payload; },
    logout: (state, action) => { state.logout = action.payload; },
    register: (state, action) => { state.register = action.payload; }
  },
});

export const { setLoading, setError, clearError, login, logout, register } = authSlice.actions;
export default authSlice.reducer;
