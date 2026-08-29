import { createSlice } from "@reduxjs/toolkit";

const initialState = {
  isSidebarOpen: true,
  isDarkMode: false,
  language: "fa",
  notifications: [],
  loading: false,
  error: null,
};

const uiSlice = createSlice({
  name: "ui",
  initialState,
  reducers: {
    toggleSidebar: (state) => { state.isSidebarOpen = !state.isSidebarOpen; },
    toggleDarkMode: (state) => { state.isDarkMode = !state.isDarkMode; },
    setLoading: (state, action) => { state.loading = action.payload; },
    setError: (state, action) => { state.error = action.payload; },
    clearError: (state) => { state.error = null; },
  },
});

export const { toggleSidebar, toggleDarkMode, setLoading, setError, clearError } = uiSlice.actions;
export default uiSlice.reducer;
