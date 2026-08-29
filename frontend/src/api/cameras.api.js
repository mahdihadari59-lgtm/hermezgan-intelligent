import { api } from "./client";

export const camerasApi = {
  list(params = {}) {
    const qs = new URLSearchParams(params).toString();
    return api.get(`/cameras/?${qs}`);
  },

  getById(id) {
    return api.get(`/cameras/${id}`);
  },

  report(data) {
    return api.post("/cameras/report", data);
  },

  nearby(lat, lng, radius = 5000) {
    return api.get(`/cameras/nearby?lat=${lat}&lng=${lng}&radius=${radius}`);
  },
};
