import subprocess
import json
import tempfile
import os
from pathlib import Path

VOSK_PATH = Path("/data/data/com.termux/files/home/hermezgan-intelligent/bandari-engine-2026/bandari-engine/speech/vosk")
MODEL_PATH = "/data/data/com.termux/files/home/hormozgan-driver-pro121-backup/backend/vosk-model-fa"

class SpeechToText:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def transcribe(self, audio_path: str):
        script = f'''
const {{ SpeechToText }} = require("{VOSK_PATH}/speech_to_text.js");
const result = new SpeechToText("{MODEL_PATH}").load().transcribeFile("{audio_path}");
console.log(JSON.stringify({{ text: result, success: true }}));
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(script)
            script_path = f.name
        try:
            result = subprocess.run(["node", script_path], cwd=str(VOSK_PATH), capture_output=True, text=True, timeout=120)
            os.unlink(script_path)
            if result.returncode == 0:
                return json.loads(result.stdout.strip())
            return {"error": result.stderr, "success": False}
        except Exception as e:
            return {"error": str(e), "success": False}

    def health_check(self):
        return {"layer": 1, "name": "Vosk STT", "available": VOSK_PATH.exists(), "status": "active"}

def get_speech_engine():
    return SpeechToText()
