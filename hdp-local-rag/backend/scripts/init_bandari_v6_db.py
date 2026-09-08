from __future__ import annotations
import asyncio
from app.services.bandari.database import engine
from app.services.bandari.models import Base

async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Bandari v6 tables ready")

if __name__ == "__main__":
    asyncio.run(main())
