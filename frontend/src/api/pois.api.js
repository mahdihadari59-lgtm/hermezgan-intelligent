import { api } from "./client";

export const poisApi = {
  nearby(params = {}) {
    const qs = new URLSearchParams(params).toString();
    return api.get(`/pois/nearby?${qs}`);
  },

  search(query, params = {}) {
    const qs = new URLSearchParams({ q: query, ...params }).toString();
    return api.get(`/pois/search?${qs}`);
  },

  categories() {
    return api.get("/pois/categories");
  },

  cities() {
    return api.get("/pois/cities");
  },

  stats() {
    return api.get("/pois/stats");
  },

  getById(id) {
    return api.get(`/pois/${id}`);
  },
};
