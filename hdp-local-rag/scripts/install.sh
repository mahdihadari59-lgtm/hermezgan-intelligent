#!/bin/bash
set -e
echo "🔧 HDP Local RAG Installer"

pkg update -y
pkg install -y python python-pip sqlite deno git

pip install -r requirements.txt

echo "✅ Installation complete. Run: ./scripts/start.sh"
