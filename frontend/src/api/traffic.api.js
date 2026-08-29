import { api } from "./client";

export const trafficApi = {
  current() {
    return api.get("/traffic/traffic");
  },

  incidents() {
    return api.get("/traffic/incidents");
  },

  stats() {
    return api.get("/traffic/stats");
  },

  predictions(roadId) {
    return api.get(`/traffic/predictions/${roadId}`);
  },

  report(data) {
    return api.post("/traffic/report", data);
  },
};
