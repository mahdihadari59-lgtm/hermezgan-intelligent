import { api } from "./client";

export const voiceApi = {
  synthesize(text, options = {}) {
    return api.post("/voice/synthesize", {
      text,
      language: options.language || "fa",
      voice: options.voice || "default",
      speed: options.speed || 1.0,
    });
  },

  status() {
    return api.get("/voice/status");
  },
};
