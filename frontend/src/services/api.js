import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5000/api',
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
