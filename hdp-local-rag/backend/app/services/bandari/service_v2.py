from fastapi import Depends
from .service import BandariServiceV6
from .database import get_db

BandariServiceV2 = BandariServiceV6

def get_bandari_service_v2(db=Depends(get_db)) -> BandariServiceV2:
    return BandariServiceV2(db)
