from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from app.models.user import UserActivity, UserAnalyticsProfile
from app.schemas.analytics_schemas import EngagementResponse, ActivityLogCreate
from app.core.database import get_db
from datetime import datetime, timedelta
import json


@router.post("/log-activity/", status_code=201)
async def log_user_activity(
    activity_data: ActivityLogCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        activity = UserActivity(
            user_id=activity_data.user_id,
            capsule_id=activity_data.capsule_id,
            activity_type=activity_data.activity_type,
            activity_details=json.dumps(activity_data.details),
            timestamp=datetime.utcnow()
        )
        db.add(activity)
        await db.commit()
        return {"status": "activity logged"}
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trends/", response_model=EngagementResponse)
async def get_engagement_trends(
    timeframe: str = "7d",
    db: AsyncSession = Depends(get_db)
):
    time_map = {
        "24h": datetime.utcnow() - timedelta(hours=24),
        "7d": datetime.utcnow() - timedelta(days=7),
        "30d": datetime.utcnow() - timedelta(days=30)
    }
    
    result = await db.execute(
        select(
            UserActivity.activity_type,
            func.count().label("count"),
            func.date_trunc('hour', UserActivity.timestamp).label("time_bucket")
        )
        .where(UserActivity.timestamp >= time_map[timeframe])
        .group_by(UserActivity.activity_type, "time_bucket")
        .order_by("time_bucket")
    )
    
    trends = {}
    for activity_type, count, bucket in result:
        if activity_type not in trends:
            trends[activity_type] = []
        trends[activity_type].append({
            "timestamp": bucket.isoformat(),
            "count": count
        })
    
    return {"timeframe": timeframe, "trends": trends}