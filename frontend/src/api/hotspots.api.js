import { api } from "./client";

export const hotspotsApi = {
  list(params = {}) {
    const qs = new URLSearchParams(params).toString();
    return api.get(`/hotspots/?${qs}`);
  },

  getById(id) {
    return api.get(`/hotspots/${id}`);
  },

  stats() {
    return api.get("/hotspots/stats");
  },
};
