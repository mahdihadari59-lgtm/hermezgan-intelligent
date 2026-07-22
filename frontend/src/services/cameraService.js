import api from './api';

const cameraService = {
  getAllCameras: async () => {
    try {
      const response = await api.get('/locations/cameras');
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },
  getCamerasByRegion: async (region) => {
    try {
      const response = await api.get('/locations/cameras', { params: { region } });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },
  reportCameraIssue: async (cameraId, issue) => {
    try {
      const response = await api.post(`/locations/cameras/${cameraId}/report`, { issue });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },
  getMockCameras: () => {
    return [
      { id: 'ba-001', name: 'چهارراه غزی', region: 'bandar-abbas', lat: 27.2158, lng: 56.2808, types: ['traffic-light', 'speed'], status: 'active', installed: '۱۴۰۳/۰۶/۱۵' },
      { id: 'ba-002', name: 'میدان سپاه (فلکه امام حسین)', region: 'bandar-abbas', lat: 27.2200, lng: 56.2850, types: ['traffic-light'], status: 'active', installed: '۱۴۰۳/۰۶/۱۰' },
      { id: 'ba-003', name: 'بلوار امام خمینی (بیمارستان محمدی)', region: 'bandar-abbas', lat: 27.2180, lng: 56.2750, types: ['speed'], status: 'active', installed: '۱۴۰۳/۰۷/۰۱' },
    ];
  },
};

export default cameraService;
