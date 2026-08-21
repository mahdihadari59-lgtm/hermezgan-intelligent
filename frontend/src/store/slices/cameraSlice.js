import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  cameras: [],
  selectedCamera: null,
  cameraFilter: 'all',
  regionFilter: null,
  regions: [
    { id: 'bandar-abbas', name: 'بندرعباس', total: 184 },
    { id: 'qeshm', name: 'قشم', total: 8 },
    { id: 'kish', name: 'کیش', total: 19 },
  ],
  cameraTypes: [
    { id: 'traffic-light', name: 'چراغ قرمز', icon: '🚦', color: '#ff4757' },
    { id: 'speed', name: 'سرعت', icon: '⚡', color: '#ffa502' },
    { id: 'plate', name: 'پلاک‌خوان', icon: '🔍', color: '#1e90ff' },
    { id: 'night-ir', name: 'IR شب', icon: '🌙', color: '#9b59b6' },
  ],
  statuses: [
    { id: 'active', name: '✅ فعال', color: '#2ed573' },
    { id: 'installing', name: '⚠️ در حال نصب', color: '#ffa502' },
    { id: 'pending', name: '🔴 نیاز فوری', color: '#ff4757' },
  ],
  isLoading: false,
  error: null,
};

const cameraSlice = createSlice({
  name: 'camera',
  initialState,
  reducers: {
    setCameras: (state, action) => { state.cameras = action.payload; },
    selectCamera: (state, action) => { state.selectedCamera = action.payload; },
    clearCameraSelection: (state) => { state.selectedCamera = null; },
    setCameraFilter: (state, action) => { state.cameraFilter = action.payload; },
    setRegionFilter: (state, action) => { state.regionFilter = action.payload; },
    updateCameraStatus: (state, action) => {
      const camera = state.cameras.find(c => c.id === action.payload.id);
      if (camera) camera.status = action.payload.status;
    },
    setLoading: (state, action) => { state.isLoading = action.payload; },
    setError: (state, action) => { state.error = action.payload; },
    clearError: (state) => { state.error = null; },
  },
});

export const {
  setCameras,
  selectCamera,
  clearCameraSelection,
  setCameraFilter,
  setRegionFilter,
  updateCameraStatus,
  setLoading,
  setError,
  clearError,
} = cameraSlice.actions;

export default cameraSlice.reducer;
