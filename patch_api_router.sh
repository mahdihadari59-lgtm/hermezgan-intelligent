#!/data/data/com.termux/files/usr/bin/bash
set -e

ROOT="$HOME/hermezgan-intelligent"

cd "$ROOT"

ROUTER="backend/app/api/v1/routers.py"
MAIN="backend/main.py"

echo "[1/2] patch routers.py..."

grep -q "from app.api.tourism import TourismAPI" "$ROUTER" || sed -i '/from fastapi import APIRouter/a\
from app.api.tourism import TourismAPI\
from app.api.hospitals import HospitalAPI\
from app.api.fuel import FuelAPI\
from app.api.poi import PoiAPI\
from app.spatial_api import SpatialDB
' "$ROUTER"

grep -q "db = SpatialDB" "$ROUTER" || sed -i '/router = APIRouter()/a\
\
db = SpatialDB("geo.db")\
tourism_api = TourismAPI(db)\
hospital_api = HospitalAPI(db)\
fuel_api = FuelAPI(db)\
poi_api = PoiAPI(db)
' "$ROUTER"

grep -q '@router.get("/map/tourism")' "$ROUTER" || cat >> "$ROUTER" <<'PY'

# ---------------- Spatial API ----------------

@router.get("/map/tourism")
def tourism():
    return tourism_api.query()

@router.get("/map/hospitals")
def hospitals():
    return hospital_api.query()

@router.get("/map/fuel")
def fuel():
    return fuel_api.query()

@router.get("/map/poi")
def poi(category: str | None = None):
    if category:
        return poi_api.query(where={"category": category})
    return poi_api.query()

PY

echo "[2/2] patch main.py..."

grep -q "from app.api.v1.routers import router as api_router" "$MAIN" || \
sed -i '/from fastapi import FastAPI/a\
from app.api.v1.routers import router as api_router
' "$MAIN"

grep -q "include_router(api_router" "$MAIN" || \
sed -i '/app = FastAPI(/,/^)/a\
\
app.include_router(api_router, prefix="/api/v1")
' "$MAIN"

echo
echo "======================================="
echo "Patch completed."
echo "======================================="
