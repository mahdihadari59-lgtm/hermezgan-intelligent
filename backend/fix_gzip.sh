#!/data/data/com.termux/files/usr/bin/bash
set -e

ROOT="$HOME/hermezgan-intelligent"

echo "Searching..."

find "$ROOT" -type f \( -name "*.py" -o -name "*.pyi" \) | while read -r f
do
    sed -i \
        -e 's/from fastapi\.middleware\.gzip import GZIPMiddleware/from starlette.middleware.gzip import GZipMiddleware/g' \
        -e 's/\bGZIPMiddleware\b/GZipMiddleware/g' \
        "$f"
done

echo
echo "Done."

grep -R "middleware.gzip" "$ROOT" --include="*.py"
echo
grep -R "GZIPMiddleware" "$ROOT" --include="*.py"

