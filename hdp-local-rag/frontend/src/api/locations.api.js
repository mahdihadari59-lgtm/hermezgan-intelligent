import { api } from "./client";

export const locationsApi = {
  search(params = {}) {
    const qs = new URLSearchParams(params).toString();
    return api.get(`/locations/search?${qs}`);
  },

  nearest(params = {}) {
    const qs = new URLSearchParams(params).toString();
    return api.get(`/locations/nearest?${qs}`);
  },

  route(params = {}) {
    const qs = new URLSearchParams(params).toString();
    return api.get(`/locations/route?${qs}`);
  },

  geocode(address) {
    return api.get(`/locations/geocode?address=${encodeURIComponent(address)}`);
  },

  reverseGeocode(lat, lng) {
    return api.get(`/locations/reverse?lat=${lat}&lng=${lng}`);
  },
};
