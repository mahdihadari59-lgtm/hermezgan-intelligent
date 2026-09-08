
import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  loading: false,
  error: null,
  data: [],
};

const uiSlice = createSlice({
  name: 'ui',
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
    toggleSidebar: (state, action) => { state.toggleSidebar = action.payload; },
    setTheme: (state, action) => { state.setTheme = action.payload; },
    addNotification: (state, action) => { state.addNotification = action.payload; }
  },
});

export const { setLoading, setError, clearError, toggleSidebar, setTheme, addNotification } = uiSlice.actions;
export default uiSlice.reducer;
