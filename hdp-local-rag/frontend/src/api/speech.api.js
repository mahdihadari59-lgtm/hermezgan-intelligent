import { api } from "./client";

export const speechApi = {
  async transcribe(audioBlob, options = {}) {
    const form = new FormData();
    form.append("audio", audioBlob, options.filename || "speech.wav");
    form.append("language", options.language || "fa");
    form.append("return_audio", String(options.returnAudio ?? false));
    form.append("use_bandari", String(options.useBandari ?? true));
    form.append("detect_intent", String(options.detectIntent ?? true));
    form.append("use_rag", String(options.useRag ?? true));

    return api.post("/speech/transcribe", form);
  },

  async process(audioBlob, options = {}) {
    const form = new FormData();
    form.append("audio", audioBlob, options.filename || "speech.wav");
    form.append("user_id", options.userId || "web_user");
    form.append("language", options.language || "fa");
    form.append("return_audio", String(options.returnAudio ?? true));
    form.append("use_bandari", String(options.useBandari ?? true));

    return api.post("/speech/process", form);
  },

  status() {
    return api.get("/speech/status");
  },
};
