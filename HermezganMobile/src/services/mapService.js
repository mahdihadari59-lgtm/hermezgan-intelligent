const mapService = {
  searchServices: async (query) => {
    const mockServices = [
      { id: 1, name: 'بیمارستان امام خمینی', type: 'hospital', lat: 27.2158, lng: 56.2808, rating: 4.8, address: 'بندرعباس', phone: '۰۷۶-۳۴۰۰۱۲۳' },
      { id: 2, name: 'رستوران تالار خلیج', type: 'restaurant', lat: 27.2200, lng: 56.2900, rating: 4.5, address: 'بندرعباس', phone: '۰۷۶-۳۲۲۲۲۲۲' },
    ];
    return mockServices;
  },
  getMockServices: () => {
    return [
      { id: 1, name: 'بیمارستان امام خمینی', type: 'hospital', lat: 27.2158, lng: 56.2808, rating: 4.8, address: 'بندرعباس', phone: '۰۷۶-۳۴۰۰۱۲۳' },
      { id: 2, name: 'رستوران تالار خلیج', type: 'restaurant', lat: 27.2200, lng: 56.2900, rating: 4.5, address: 'بندرعباس', phone: '۰۷۶-۳۲۲۲۲۲۲' },
    ];
  },
};

export default mapService;
