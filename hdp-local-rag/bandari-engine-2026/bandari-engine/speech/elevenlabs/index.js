// index.js — کلاینت TTS برای ElevenLabs
// از fetch داخلی Node (v18+) استفاده می‌کنه، بدون نیاز به پکیج npm اضافه.

const fs = require("fs");

const ELEVENLABS_API_KEY = process.env.ELEVENLABS_API_KEY;
const DEFAULT_VOICE_ID = process.env.ELEVENLABS_VOICE_ID || "21m00Tcm4TlvDq8ikWAM"; // Rachel (پیش‌فرض)
const API_BASE = "https://api.elevenlabs.io/v1";

class ElevenLabsTTS {
  constructor({ apiKey = ELEVENLABS_API_KEY, voiceId = DEFAULT_VOICE_ID } = {}) {
    if (!apiKey) {
      throw new Error(
        "ELEVENLABS_API_KEY تنظیم نشده. توی .env یا env vars ست کن."
      );
    }
    this.apiKey = apiKey;
    this.voiceId = voiceId;
  }

  /**
   * متن رو به صدا تبدیل می‌کنه و به‌صورت Buffer (MP3) برمی‌گردونه.
   * @param {string} text
   * @param {object} options - { voiceId, modelId, stability, similarityBoost }
   */
  async synthesize(text, options = {}) {
    const voiceId = options.voiceId || this.voiceId;
    const url = `${API_BASE}/text-to-speech/${voiceId}`;

    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "xi-api-key": this.apiKey,
        Accept: "audio/mpeg",
      },
      body: JSON.stringify({
        text,
        model_id: options.modelId || "eleven_multilingual_v2",
        voice_settings: {
          stability: options.stability ?? 0.5,
          similarity_boost: options.similarityBoost ?? 0.75,
        },
      }),
    });

    if (!response.ok) {
      const errText = await response.text();
      throw new Error(`ElevenLabs API خطا داد (${response.status}): ${errText}`);
    }

    const arrayBuffer = await response.arrayBuffer();
    return Buffer.from(arrayBuffer);
  }

  /** متن رو به صدا تبدیل و مستقیم توی یک فایل mp3 ذخیره می‌کنه. */
  async synthesizeToFile(text, outputPath, options = {}) {
    const audioBuffer = await this.synthesize(text, options);
    fs.writeFileSync(outputPath, audioBuffer);
    return outputPath;
  }

  /** لیست صداهای موجود توی اکانت رو برمی‌گردونه. */
  async listVoices() {
    const response = await fetch(`${API_BASE}/voices`, {
      headers: { "xi-api-key": this.apiKey },
    });
    if (!response.ok) {
      throw new Error(`دریافت لیست صداها شکست خورد (${response.status})`);
    }
    const data = await response.json();
    return data.voices;
  }
}

module.exports = { ElevenLabsTTS, DEFAULT_VOICE_ID };
