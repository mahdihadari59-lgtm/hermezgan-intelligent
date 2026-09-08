#!/bin/bash
set -e

export HDP_DB_PATH="${HDP_DB_PATH:-./db/hdp_master.db}"
export PYTHON_API="http://localhost:8000"

echo "🚀 Starting HDP Local RAG..."

python api/main.py &
PY_PID=$!

sleep 3

deno task --config deno/deno.json start &
DENO_PID=$!

echo "✅ Services running:"
echo "   Python API: http://localhost:8000"
echo "   Deno Web:   http://localhost:3000"
echo "   Press Ctrl+C to stop"

trap "kill $PY_PID $DENO_PID" EXIT
wait
