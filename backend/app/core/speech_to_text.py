"""
speech_to_text.py — پل پایتون به Vosk STT (از طریق Node.js bridge تست‌شده)

بریج واقعی: backend/tests/vosk/stt_cli.js
مدل: مسیرش از env var VOSK_MODEL_PATH خونده می‌شه، با fallback به
     ~/.local/share/vosk-model-fa (همونی که با unzip vosk-model-small-fa-0.42.zip ساختیم)
"""
import subprocess
import json
import os
from pathlib import Path

# مسیر backend را نسبت به همین فایل پیدا می‌کنیم (app/core/speech_to_text.py -> backend/)
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
STT_CLI_PATH = BACKEND_DIR / "tests" / "vosk" / "stt_cli.js"

DEFAULT_MODEL_PATH = str(Path.home() / ".local" / "share" / "vosk-model-fa")
MODEL_PATH = os.getenv("VOSK_MODEL_PATH", DEFAULT_MODEL_PATH)


class SpeechToText:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def transcribe(self, audio_path: str) -> dict:
        """تبدیل فایل wav به متن با فراخوانی stt_cli.js"""
        if not STT_CLI_PATH.exists():
            return {"success": False, "error": f"stt_cli.js پیدا نشد: {STT_CLI_PATH}"}
        if not os.path.exists(MODEL_PATH):
            return {"success": False, "error": f"مدل Vosk پیدا نشد: {MODEL_PATH}"}
        if not os.path.exists(audio_path):
            return {"success": False, "error": f"فایل صوتی پیدا نشد: {audio_path}"}

        env = os.environ.copy()
        env["VOSK_MODEL_PATH"] = MODEL_PATH

        try:
            result = subprocess.run(
                ["node", str(STT_CLI_PATH), audio_path],
                cwd=str(STT_CLI_PATH.parent),
                capture_output=True,
                text=True,
                timeout=120,
                env=env,
            )
            # stt_cli.js لاگ‌های اضافی (✅ ...) رو هم روی stdout می‌ریزه؛
            # فقط آخرین خط، JSON خالص خروجی واقعیه.
            lines = [l for l in result.stdout.strip().splitlines() if l.strip()]
            if not lines:
                return {"success": False, "error": result.stderr or "خروجی خالی از stt_cli.js"}
            last_line = lines[-1]
            return json.loads(last_line)
        except json.JSONDecodeError as e:
            return {"success": False, "error": f"خطای parse خروجی JSON: {e}"}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "timeout در تبدیل گفتار به متن"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def health_check(self) -> dict:
        return {
            "layer": 1,
            "name": "Vosk STT (Node bridge)",
            "stt_cli_exists": STT_CLI_PATH.exists(),
            "model_path": MODEL_PATH,
            "model_exists": os.path.exists(MODEL_PATH),
            "available": STT_CLI_PATH.exists() and os.path.exists(MODEL_PATH),
            "status": "active" if (STT_CLI_PATH.exists() and os.path.exists(MODEL_PATH)) else "unavailable",
        }


def get_speech_engine() -> SpeechToText:
    return SpeechToText()
