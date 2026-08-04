import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL
    ? `${process.env.REACT_APP_API_URL}/api/v1`
    : 'http://localhost:8000/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;


# STAGE8_PATCH

// HDP Stage 8 Integration
export const IntegrationService = {
  checkHealth: () => apiService.get('/health'),
  getSystemStatus: () => apiService.get('/system/status'),
  getVersion: () => apiService.get('/version'),
};
