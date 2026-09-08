#!/bin/bash
termux-setup-storage
pkg update && pkg upgrade -y
pkg install -y python python-pip sqlite deno git curl

mkdir -p ~/hdp-local-rag && cd ~/hdp-local-rag
mkdir -p db

echo "📱 Termux setup complete!"
echo "Next: copy your database to db/hdp_master.db and run ./scripts/install.sh"
