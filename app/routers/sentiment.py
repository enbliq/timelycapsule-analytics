from fastapi import APIRouter, Depends, Body, HTTPException
from app.services.analytics_engine import AnalyticsProcessor
from app.schemas.analytics_schemas import SentimentRequest, SentimentResponse
from app.models.capsule import CapsuleContent
from app.core.database import get_db
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/sentiment", tags=["Sentiment Analysis"])

class ModerationRequest(BaseModel):
    text: str
    user_id: str  # Should come from auth in real implementation
    message_id: str

@router.post("/moderation/analyze")
async def analyze_content(request: ModerationRequest):
    analysis = AnalyticsProcessor.analyze_moderation_score(request.text)
    
    # Log flagged content
    if analysis['status'] != 'safe':
        log_entry = {
            "user_id": request.user_id,
            "message_id": request.message_id,
            "toxicity_score": analysis['toxicity_score'],
            "flagged_words": analysis['flagged_words'],
            "timestamp": datetime.now()
        }
        await db.moderation_logs.insert_one(log_entry)
    
    return analysis

@router.get("/moderation/reports")
async def get_reports():
    reports = await db.moderation_logs.aggregate([
        {
            "$group": {
                "_id": {
                    "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
                    "status": "$status"
                },
                "count": {"$sum": 1},
                "avg_score": {"$avg": "$toxicity_score"}
            }
        }
    ]).to_list(length=None)
    return {"reports": reports}

@router.post("/analyze-text/", response_model=SentimentResponse)
async def analyze_free_text(
    request: SentimentRequest = Body(...)
):
    return AnalyticsProcessor.analyze_sentiment(request.text)

@router.post("/process-capsule/{capsule_id}/")
async def process_capsule_sentiment(
    capsule_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(CapsuleContent).where(CapsuleContent.original_capsule_id == capsule_id)
    )
    capsule = result.scalars().first()
    
    if not capsule:
        raise HTTPException(status_code=404, detail="Capsule not found")
    
    analysis = AnalyticsProcessor.analyze_sentiment(capsule.content)
    
    capsule.sentiment_score = analysis["polarity"]
    await db.commit()
    
    return {
        "capsule_id": capsule_id,
        "sentiment": analysis,
        "status": "updated"
    }

@router.get("/full-dashboard")
async def get_full_dashboard(
    timeframe: str = "7d",
    db: AsyncSession = Depends(get_db)
):
    # Get engagement data
    engagement = await get_engagement_trends(timeframe, db)
    
    # Get sentiment data
    result = await db.execute(
        select(CapsuleContent.sentiment_score)
    )
    sentiments = [row[0] for row in result.all()]
    
    # Generate word cloud
    content_result = await db.execute(select(CapsuleContent.content))
    wordcloud = AnalyticsProcessor.generate_wordcloud(" ".join(row[0] for row in content_result))
    
    return {
        "engagement_chart": engagement,
        "sentiment_histogram": np.histogram(sentiments, bins=10),
        "wordcloud": wordcloud,
        "top_recommendations": await get_recommendations(db)
    }