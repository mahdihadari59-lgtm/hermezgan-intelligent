#!/data/data/com.termux/files/usr/bin/bash

set -e

PROJECT="$HOME/hermezgan-intelligent"

cd "$PROJECT"

echo "===================================="
echo "HDP Smart Organizer"
echo "===================================="

mkdir -p frontend/src/components/map
mkdir -p frontend/src/components/layers
mkdir -p frontend/src/api
mkdir -p frontend/src/hooks
mkdir -p frontend/src/utils
mkdir -p backend/app
mkdir -p backend/scripts
mkdir -p database/migrations
mkdir -p docs/imported

echo
echo "[1/6] تبدیل فایل‌های JSX..."

for f in *.jsx.txt
do
    [ -f "$f" ] || continue
    mv "$f" "${f%.txt}"
done

echo
echo "[2/6] انتقال لایه‌های نقشه..."

for f in \
CameraLayer.jsx \
TrafficLayer.jsx \
WeatherLayer.jsx \
HospitalLayer.jsx \
FuelLayer.jsx \
HeatmapLayer.jsx \
GeoTiffLayer.jsx \
VectorTileLayer.jsx \
TourismLayer.jsx \
OfflineTileLayer.jsx
do
    [ -f "$f" ] && mv -f "$f" frontend/src/components/layers/
done

echo
echo "[3/6] انتقال هسته نقشه..."

for f in \
MapEngine.jsx \
RoutingManager.jsx \
ClusterManager.jsx \
MarkerManager.jsx \
DrawTools.jsx \
OfflineManager.jsx
do
    [ -f "$f" ] && mv -f "$f" frontend/src/components/map/
done

echo
echo "[4/6] انتقال فایل‌های JavaScript..."

[ -f mapApi.js ] && mv -f mapApi.js frontend/src/api/
[ -f useLiveChannel.js ] && mv -f useLiveChannel.js frontend/src/hooks/

for f in offlineCache.js popupContent.js
do
    [ -f "$f" ] && mv -f "$f" frontend/src/utils/
done

echo
echo "[5/6] انتقال Backend..."

for f in \
server.py \
spatial_api.py
do
    [ -f "$f" ] && mv -f "$f" backend/app/
done

for f in \
migrate-1.py \
seed_data.py
do
    [ -f "$f" ] && mv -f "$f" backend/scripts/
done

[ -f schema-2.sql ] && mv -f schema-2.sql database/migrations/

echo
echo "[6/6] انتقال مستندات..."

[ -f CHANGES.md ] && mv -f CHANGES.md docs/imported/
[ -f README-7.md ] && mv -f README-7.md docs/imported/

echo
echo "===================================="
echo "پایان انتقال"
echo "===================================="

echo
echo "ساختار فایل‌های منتقل‌شده:"
find frontend/src -maxdepth 4 -type f | sort

echo
find backend -maxdepth 3 -type f | sort

echo
find database -maxdepth 3 -type f | sort

echo
echo "فایل‌های باقی‌مانده در ریشه پروژه:"
find . -maxdepth 1 -type f
