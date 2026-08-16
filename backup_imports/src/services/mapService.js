import api from './api';

const mapService = {
  getNearbyServices: async (latitude, longitude, serviceType = null, radius = 5) => {
    try {
      const response = await api.get('/locations/nearest', { params: { latitude, longitude, service_type: serviceType, radius } });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },
  searchLocations: async (query, latitude = null, longitude = null) => {
    try {
      const response = await api.get('/locations/search', { params: { query, latitude, longitude } });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },
  getRoute: async (startLat, startLng, endLat, endLng) => {
    try {
      const response = await api.get('/locations/route', { params: { start_lat: startLat, start_lng: startLng, end_lat: endLat, end_lng: endLng } });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },
  getUserLocation: () => {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) reject('Geolocation not supported');
      navigator.geolocation.getCurrentPosition(
        (position) => resolve({ lat: position.coords.latitude, lng: position.coords.longitude, accuracy: position.coords.accuracy }),
        (error) => reject(error.message)
      );
    });
  },
  getMockServices: () => {
    return [
      { id: 1, name: 'بیمارستان فوق‌تخصصی کودکان', type: 'hospital', lat: 27.2158, lng: 56.2808, rating: 4.8, distance: 2.3, address: 'خیابان شهید رجایی، بندرعباس', phone: '۰۷۶-۳۴۰۰۱۲۳', openHours: '۲۴/۷' },
      { id: 2, name: 'رستوران تالار خلیج', type: 'restaurant', lat: 27.2200, lng: 56.2900, rating: 4.5, distance: 1.2, address: 'خیابان ولیعصر، بندرعباس', phone: '۰۷۶-۳۲۲۲۲۲۲', openHours: '۱۲:۰۰ - ۲۳:۰۰' },
    ];
  },
};

export default mapService;
