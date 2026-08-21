
import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  loading: false,
  error: null,
  data: [],
};

const cameraSlice = createSlice({
  name: 'camera',
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
    setCameras: (state, action) => { state.setCameras = action.payload; },
    selectCamera: (state, action) => { state.selectCamera = action.payload; }
  },
});

export const { setLoading, setError, clearError, setCameras, selectCamera } = cameraSlice.actions;
export default cameraSlice.reducer;
