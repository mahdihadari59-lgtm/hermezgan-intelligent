import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  center: { lat: 27.2158, lng: 56.2808 },
  markers: [],
  selectedMarker: null,
};

const mapSlice = createSlice({
  name: 'map',
  initialState,
  reducers: {
    setMapCenter: (state, action) => {
      state.center = action.payload;
    },
    setMarkers: (state, action) => {
      state.markers = action.payload;
    },
    selectMarker: (state, action) => {
      state.selectedMarker = action.payload;
    },
  },
});

export const { setMapCenter, setMarkers, selectMarker } = mapSlice.actions;
export default mapSlice.reducer;
