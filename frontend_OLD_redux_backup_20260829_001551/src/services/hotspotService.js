import api from './api';

const hotspotService = {
  getHotspots: async () => {
    try {
      const response = await api.get('/locations/hotspots');
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },
  getHotspotsByType: async (type) => {
    try {
      const response = await api.get('/locations/hotspots', { params: { type } });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },
  getNearbyHotspots: async (latitude, longitude, radius = 5) => {
    try {
      const response = await api.get('/locations/hotspots/nearby', { params: { latitude, longitude, radius } });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },
  reportHotspot: async (data) => {
    try {
      const response = await api.post('/locations/hotspots/report', data);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },
  getMockHotspots: () => {
    return [
      { id: 101, type: 'accident', lat: 27.2200, lng: 56.2850, title: 'تصادف در تقاطع خیابان شهید رجایی', description: 'تصادف بین دو خودرو - ترافیک سنگین', severity: 'high', reportedAt: '۱۵ دقیقه پیش', reportedBy: 'کاربران', status: 'active' },
      { id: 102, type: 'traffic', lat: 27.2180, lng: 56.2750, title: 'ترافیک سنگین خیابان ولیعصر', description: 'ترافیک بسیار سنگین - از جمهوری تا شهید رجایی', severity: 'medium', reportedAt: '۲۰ دقیقه پیش', reportedBy: 'سیستم ترافیکی', status: 'active' },
      { id: 103, type: 'danger', lat: 27.2250, lng: 56.2900, title: 'مناطق خطرناک - عدم رعایت علائم راهنمایی', description: 'منطقه‌ای که رانندگان کم سرعت را رعایت نمی‌کنند', severity: 'high', reportedAt: '۳۰ دقیقه پیش', reportedBy: 'پلیس راهور', status: 'active' },
      { id: 104, type: 'construction', lat: 27.2100, lng: 56.2800, title: 'ساخت و ساز خیابان تجریش', description: 'ساخت و ساز جاده - دو خط مسدود', severity: 'low', reportedAt: '۲ ساعت پیش', reportedBy: 'شهرداری', status: 'active' },
      { id: 105, type: 'accident', lat: 27.2300, lng: 56.2700, title: 'تصادف در بلوار فردوسی', description: 'خودروی پارک شده و موتورسیکلت', severity: 'medium', reportedAt: '۴۵ دقیقه پیش', reportedBy: 'کاربران', status: 'resolved' },
    ];
  },
};

export default hotspotService;
