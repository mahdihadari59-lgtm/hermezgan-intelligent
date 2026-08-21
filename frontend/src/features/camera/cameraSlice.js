import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  cameras: [],
  selectedCamera: null,
  cameraFilter: null,
  regionFilter: null,
  isLoading: false,
  error: null,
};

const cameraSlice = createSlice({
  name: 'camera',
  initialState,
  reducers: {
    setCameras: (state, action) => {
      state.cameras = action.payload;
    },
    selectCamera: (state, action) => {
      state.selectedCamera = action.payload;
    },
    clearSelection: (state) => {
      state.selectedCamera = null;
    },
    clearCameraSelection: (state) => {
      state.selectedCamera = null;
    },
    setCameraFilter: (state, action) => {
      state.cameraFilter = action.payload;
    },
    setRegionFilter: (state, action) => {
      state.regionFilter = action.payload;
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

export const {
  setCameras,
  selectCamera,
  clearSelection,
  clearCameraSelection,
  setCameraFilter,
  setRegionFilter,
  setLoading,
  setError,
  clearError,
} = cameraSlice.actions;

export default cameraSlice.reducer;
