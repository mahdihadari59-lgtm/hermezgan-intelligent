import subprocess
import json
import tempfile
import os
from pathlib import Path

# Make paths configurable via env vars
VOSK_PATH = Path(os.environ.get("VOSK_PATH", "/data/data/com.termux/files/home/hermezgan-intelligent/bandari-engine-2026/bandari-engine/speech/vosk"))
MODEL_PATH = os.environ.get("VOSK_MODEL_PATH", "/data/data/com.termux/files/home/hormozgan-driver-pro121-backup/backend/vosk-model-fa")

class SpeechToText:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def transcribe(self, audio_path: str):
        # Use Node Vosk wrapper under VOSK_PATH if present
        script = f'''
const {{ SpeechToText }} = require("{VOSK_PATH.as_posix()}/speech_to_text.js");
(async () => {{
  try {{
    const engine = new SpeechToText("{MODEL_PATH}");
    // load may be sync or async depending on implementation
    if (typeof engine.load === 'function') {{
      await engine.load();
    }}
    const result = await engine.transcribeFile("{audio_path}");
    console.log(JSON.stringify({{ text: result, success: true }}));
  }} catch (e) {{
    console.log(JSON.stringify({{ success: false, error: String(e) }}));
  }}
}})();
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(script)
            script_path = f.name
        try:
            result = subprocess.run(["node", script_path], cwd=str(VOSK_PATH), capture_output=True, text=True, timeout=120)
            out = result.stdout.strip()
            if result.returncode == 0 and out:
                try:
                    obj = json.loads(out.splitlines()[-1])
                    if isinstance(obj, dict) and obj.get("success"):
                        # prefer obj["text"] string
                        return obj.get("text", "")
                    # fallback: whole stdout
                    return out
                except Exception:
                    return out
            # on error, return empty string (caller expects str)
            return ""
        except Exception as e:
            return ""

    def health_check(self):
        return {"layer": 1, "name": "Vosk STT", "available": VOSK_PATH.exists(), "status": "active"}

def get_speech_engine():
    return SpeechToText()