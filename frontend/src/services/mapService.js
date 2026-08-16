import api from './api';

const mapService = {
  // Get nearby services
  getNearbyServices: async (latitude, longitude, serviceType = null, radius = 5) => {
    try {
      const response = await api.get('/locations/nearest', {
        params: {
          latitude,
          longitude,
          service_type: serviceType,
          radius,
        },
      });
      return response;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Search locations
  searchLocations: async (query, latitude = null, longitude = null) => {
    try {
      const response = await api.get('/locations/search', {
        params: {
          query,
          latitude,
          longitude,
        },
      });
      return response;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Get route
  getRoute: async (startLat, startLng, endLat, endLng) => {
    try {
      const response = await api.get('/locations/route', {
        params: {
          start_lat: startLat,
          start_lng: startLng,
          end_lat: endLat,
          end_lng: endLng,
        },
      });
      return response;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Get user geolocation
  getUserLocation: () => {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject('Geolocation not supported');
      }
      navigator.geolocation.getCurrentPosition(
        (position) => {
          resolve({
            lat: position.coords.latitude,
            lng: position.coords.longitude,
            accuracy: position.coords.accuracy,
          });
        },
        (error) => {
          reject(error.message);
        }
      );
    });
  },

  // Mock data for testing
  getMockServices: () => {
    return [
      {
        id: 1,
        name: 'بیمارستان فوق‌تخصصی کودکان',
        type: 'hospital',
        lat: 27.2158,
        lng: 56.2808,
        rating: 4.8,
        distance: 2.3,
        address: 'خیابان شهید رجایی، بندرعباس',
        phone: '۰۷۶-۳۴۰۰۱۲۳',
        openHours: '۲۴/۷',
      },
      {
        id: 2,
        name: 'رستوران تالار خلیج',
        type: 'restaurant',
        lat: 27.2200,
        lng: 56.2900,
        rating: 4.5,
        distance: 1.2,
        address: 'خیابان ولیعصر، بندرعباس',
        phone: '۰۷۶-۳۲۲۲۲۲۲',
        openHours: '۱۲:۰۰ - ۲۳:۰۰',
      },
      {
        id: 3,
        name: 'تاکسی آنلاین الفردوس',
        type: 'taxi',
        lat: 27.2300,
        lng: 56.2700,
        rating: 4.6,
        distance: 0.8,
        address: 'ایستگاه تاکسی مرکزی',
        phone: '۰۷۶-۹۱۱۱۱۱۱۱',
        openHours: '۲۴/۷',
      },
      {
        id: 4,
        name: 'داروخانه شفابخش',
        type: 'pharmacy',
        lat: 27.2100,
        lng: 56.2750,
        rating: 4.3,
        distance: 1.5,
        address: 'خیابان تجریش، بندرعباس',
        phone: '۰۷۶-۳۱۱۱۱۱۱',
        openHours: '۸:۰۰ - ۲۲:۰۰',
      },
      {
        id: 5,
        name: 'مدرسه فرزانگاه',
        type: 'school',
        lat: 27.2250,
        lng: 56.2850,
        rating: 4.7,
        distance: 2.1,
        address: 'خیابان دانشگاه، بندرعباس',
        phone: '۰۷۶-۳۳۳۳۳۳۳',
        openHours: '۷:۳۰ - ۱۴:۰۰',
      },
    ];
  },
};

export default mapService;
