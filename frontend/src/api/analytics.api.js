import { api } from "./client";

export const analyticsApi = {
  dashboard() {
    return api.get("/analytics/dashboard");
  },

  traffic(params = {}) {
    const qs = new URLSearchParams(params).toString();
    return api.get(`/analytics/traffic?${qs}`);
  },

  usage(params = {}) {
    const qs = new URLSearchParams(params).toString();
    return api.get(`/analytics/usage?${qs}`);
  },

  report(type, data) {
    return api.post(`/analytics/${type}`, data);
  },
};
