from fastapi import APIRouter

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/stats")
async def get_statistics():
    return {
        "totalUsers": 1234,
        "activeUsers": 856,
        "totalServices": 567,
        "completedQueries": 3421
    }

@router.get("/user-growth")
async def get_user_growth(time_filter: str = "weekly"):
    return {
        "data": [
            {"date": "۱۵ فروردین", "users": 120, "queries": 240},
            {"date": "۱۶ فروردین", "users": 132, "queries": 221}
        ]
    }
