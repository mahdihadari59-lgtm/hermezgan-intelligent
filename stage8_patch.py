#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HDP STAGE 8
Unified Integration Patch

Author : ChatGPT
Target : Termux
Project : hermezgan-intelligent

این اسکریپت هیچ موتور جدیدی ایجاد نمی‌کند.
فقط فایل‌های موجود را به هم متصل می‌کند.
"""

from __future__ import annotations

import os
import sys
import json
import shutil
import hashlib
import sqlite3
import subprocess
import platform

from pathlib import Path
from datetime import datetime

# -------------------------------------------------------
# PROJECT PATHS
# -------------------------------------------------------

HOME = Path.home()

PROJECT = HOME / "hermezgan-intelligent"

BACKEND = PROJECT / "backend"

FRONTEND = PROJECT / "frontend"

MOBILE = PROJECT / "mobile"

BANDARI = PROJECT / "bandari-engine-2026" / "bandari-engine"

DATA = BACKEND / "data"

DATABASE = DATA / "hdp_v2.db"

BACKUP_DIR = PROJECT / "_stage8_backup"

PATCH_DIR = PROJECT / "_stage8_patch"

LOG_DIR = PROJECT / "_logs"

REPORT_DIR = PROJECT / "_reports"

# -------------------------------------------------------
# COLORS
# -------------------------------------------------------

GREEN = "\033[92m"
RED = "\033[91m"
BLUE = "\033[94m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RESET = "\033[0m"

# -------------------------------------------------------
# LOGGER
# -------------------------------------------------------

class Logger:

    def __init__(self):

        LOG_DIR.mkdir(exist_ok=True)

        self.file = LOG_DIR / "stage8.log"

    def _write(self, text):

        now = datetime.now().strftime("%H:%M:%S")

        with open(self.file, "a", encoding="utf8") as f:

            f.write(f"[{now}] {text}\n")

    def info(self, msg):

        print(f"{GREEN}[INFO]{RESET} {msg}")

        self._write(msg)

    def warn(self, msg):

        print(f"{YELLOW}[WARN]{RESET} {msg}")

        self._write(msg)

    def error(self, msg):

        print(f"{RED}[ERROR]{RESET} {msg}")

        self._write(msg)

log = Logger()

# -------------------------------------------------------
# BACKUP
# -------------------------------------------------------

class BackupManager:

    def __init__(self):

        BACKUP_DIR.mkdir(exist_ok=True)

    def backup(self, file):

        if not file.exists():

            return

        t = datetime.now().strftime("%Y%m%d_%H%M%S")

        dst = BACKUP_DIR / f"{file.name}.{t}.bak"

        shutil.copy2(file, dst)

        log.info(f"Backup : {dst.name}")

backup = BackupManager()

# -------------------------------------------------------
# HASH
# -------------------------------------------------------

def sha(path):

    if not path.exists():

        return None

    h = hashlib.sha256()

    with open(path, "rb") as f:

        while True:

            b = f.read(65536)

            if not b:

                break

            h.update(b)

    return h.hexdigest()

# -------------------------------------------------------
# EXEC
# -------------------------------------------------------

def run(cmd, cwd=None):

    return subprocess.run(

        cmd,

        cwd=cwd,

        capture_output=True,

        text=True

    )

# -------------------------------------------------------
# CHECK TERMUX
# -------------------------------------------------------

def check_termux():

    log.info("Checking environment")

    if "com.termux" not in str(Path.home()):

        log.warn("Termux path not detected")

    py = platform.python_version()

    log.info(f"Python : {py}")

    node = run(["node", "--version"])

    if node.returncode == 0:

        log.info(node.stdout.strip())

    else:

        log.error("NodeJS not installed")

    git = run(["git", "--version"])

    if git.returncode == 0:

        log.info(git.stdout.strip())

# -------------------------------------------------------
# PROJECT CHECK
# -------------------------------------------------------

def check_project():

    log.info("Scanning project")

    required = [

        PROJECT,

        BACKEND,

        BANDARI,

        DATABASE

    ]

    ok = True

    for p in required:

        if p.exists():

            log.info(f"FOUND : {p}")

        else:

            log.error(f"MISSING : {p}")

            ok = False

    return ok

# -------------------------------------------------------
# SQLITE CHECK
# -------------------------------------------------------

def check_database():

    if not DATABASE.exists():

        log.error("Database missing")

        return False

    try:

        con = sqlite3.connect(DATABASE)

        cur = con.cursor()

        cur.execute("SELECT name FROM sqlite_master")

        rows = cur.fetchall()

        log.info(f"Tables : {len(rows)}")

        con.close()

        return True

    except Exception as e:

        log.error(str(e))

        return False

# -------------------------------------------------------
# PATCH HELPER
# -------------------------------------------------------

class PatchFile:

    @staticmethod
    def append(file, text):

        backup.backup(file)

        if file.exists():

            data = file.read_text(encoding="utf8")

        else:

            data = ""

        if "STAGE8_PATCH" in data:

            log.warn(f"Already patched : {file}")

            return

        data += "\n\n# STAGE8_PATCH\n"

        data += text

        file.parent.mkdir(parents=True, exist_ok=True)

        file.write_text(data, encoding="utf8")

        log.info(f"Patched : {file}")

    @staticmethod
    def replace(file, old, new):

        backup.backup(file)

        if not file.exists():

            log.error(f"File not found: {file}")

            return

        data = file.read_text(encoding="utf8")

        if old not in data:

            log.warn(f"Pattern not found: {file}")

            return

        data = data.replace(old, new)

        file.write_text(data, encoding="utf8")

        log.info(f"Replaced in : {file}")

# -------------------------------------------------------
# REPORT
# -------------------------------------------------------

def report():

    REPORT_DIR.mkdir(exist_ok=True)

    f = REPORT_DIR / "scan.json"

    result = {

        "project": str(PROJECT),

        "database": DATABASE.exists(),

        "backend": BACKEND.exists(),

        "bandari": BANDARI.exists(),

        "time": datetime.now().isoformat()

    }

    with open(f, "w", encoding="utf8") as fp:

        json.dump(result, fp, indent=4, ensure_ascii=False)

    log.info("Report created")

# -------------------------------------------------------
# INTEGRATION PATCHES
# -------------------------------------------------------

def apply_patches():

    log.info("Applying integration patches...")

    main_py = BACKEND / "main.py"
    if main_py.exists():
        PatchFile.replace(
            main_py,
            "from engine.hybrid.hybrid_engine import HybridEngine",
            "from engine.hybrid.hybrid_engine import HybridEngine  # STAGE8"
        )

    config_py = BACKEND / "app" / "core" / "config.py"
    if config_py.exists():
        PatchFile.replace(
            config_py,
            'CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5000"]',
            'CORS_ORIGINS: List[str] = [\n    "http://localhost:3000",\n    "http://localhost:5000",\n    "http://127.0.0.1:3000",\n    "http://127.0.0.1:5000",\n]'
        )

    api_js = FRONTEND / "src" / "services" / "api.js"
    if api_js.exists():
        PatchFile.append(
            api_js,
            """
// HDP Stage 8 Integration
export const IntegrationService = {
  checkHealth: () => apiService.get('/health'),
  getSystemStatus: () => apiService.get('/system/status'),
  getVersion: () => apiService.get('/version'),
};
"""
        )

    bridge_py = BACKEND / "app" / "bridge" / "bandari_bridge.py"
    if not bridge_py.exists():
        bridge_py.parent.mkdir(parents=True, exist_ok=True)
        bridge_py.write_text("""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

\"\"\"
Bandari Engine Bridge
Connects Bandari dialect engine to HDP backend
\"\"\"

import sys
from pathlib import Path

BANDARI_PATH = Path.home() / "hermezgan-intelligent" / "bandari-engine-2026" / "bandari-engine"

if BANDARI_PATH.exists():
    sys.path.insert(0, str(BANDARI_PATH))

try:
    from bandari_core import BandariEngine
    BANDARI_ENGINE = BandariEngine()
except ImportError:
    BANDARI_ENGINE = None
    print("Bandari engine not available")

def translate_to_bandari(text):
    if BANDARI_ENGINE:
        return BANDARI_ENGINE.translate(text)
    return text

def translate_to_persian(text):
    if BANDARI_ENGINE:
        return BANDARI_ENGINE.to_persian(text)
    return text
""", encoding="utf8")
        log.info("Created bandari bridge")

    env_file = BACKEND / ".env"
    if not env_file.exists():
        env_file.write_text("""
# HDP Backend Environment
ENVIRONMENT=development
DEBUG=True
API_HOST=0.0.0.0
API_PORT=8000
DATABASE_PATH=data/hdp_v2.db
HDP_DB_PATH=data/hdp_v2.db
CORS_ORIGINS=["http://localhost:3000","http://localhost:5000"]
LOG_LEVEL=INFO
""", encoding="utf8")
        log.info("Created .env file")

# -------------------------------------------------------
# MAIN
# -------------------------------------------------------

def main():

    print()
    print("=" * 60)
    print("HDP STAGE 8")
    print("Unified Integration")
    print("=" * 60)

    check_termux()

    if not check_project():
        sys.exit(1)

    if not check_database():
        sys.exit(1)

    apply_patches()

    report()

    print()
    print("=" * 60)
    print(f"{GREEN}✅ Stage 8 Complete{RESET}")
    print("=" * 60)
    print()
    print(f"📁 Backup: {BACKUP_DIR}")
    print(f"📁 Logs: {LOG_DIR}")
    print(f"📁 Reports: {REPORT_DIR}")
    print()


if __name__ == "__main__":
    main()
