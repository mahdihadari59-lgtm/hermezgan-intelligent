// src/services/mapApi.js
// Added endpoints needed by the fixed layers (getWindData, getTourismSites,
// reportCameraIssue) and consistent bounds-param handling.

import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

function boundsParams(bounds) {
  if (!bounds) return {};
  return {
    north: bounds.getNorth(),
    south: bounds.getSouth(),
    east: bounds.getEast(),
    west: bounds.getWest(),
  };
}

export const mapApi = {
  getTrafficData: async (bounds) => {
    try {
      const { data } = await axios.get(`${API_BASE}/map/traffic`, { params: boundsParams(bounds) });
      return data;
    } catch (error) {
      console.error('Error fetching traffic:', error);
      return [];
    }
  },

  getCameras: async () => {
    try {
      const { data } = await axios.get(`${API_BASE}/map/cameras`);
      return data;
    } catch (error) {
      console.error('Error fetching cameras:', error);
      return [];
    }
  },

  reportCameraIssue: async (cameraId) => {
    try {
      await axios.post(`${API_BASE}/map/cameras/${cameraId}/report`);
      return true;
    } catch (error) {
      console.error('Error reporting camera issue:', error);
      return false;
    }
  },

  getHospitals: async () => {
    try {
      const { data } = await axios.get(`${API_BASE}/map/hospitals`);
      return data;
    } catch (error) {
      console.error('Error fetching hospitals:', error);
      return [];
    }
  },

  getFuelStations: async () => {
    try {
      const { data } = await axios.get(`${API_BASE}/map/fuel`);
      return data;
    } catch (error) {
      console.error('Error fetching fuel stations:', error);
      return [];
    }
  },

  getTourismSites: async () => {
    try {
      const { data } = await axios.get(`${API_BASE}/map/tourism`);
      return data;
    } catch (error) {
      console.error('Error fetching tourism sites:', error);
      return [];
    }
  },

  getWindData: async (bounds) => {
    try {
      const { data } = await axios.get(`${API_BASE}/map/weather/wind`, { params: boundsParams(bounds) });
      return data; // expected shape: leaflet-velocity GeoJSON feature
    } catch (error) {
      console.error('Error fetching wind data:', error);
      return null;
    }
  },

  getRoute: async (start, end) => {
    try {
      const { data } = await axios.get(`${API_BASE}/map/route`, {
        params: { start_lat: start.lat, start_lng: start.lng, end_lat: end.lat, end_lng: end.lng },
      });
      return data;
    } catch (error) {
      console.error('Error fetching route:', error);
      return null;
    }
  },
};
