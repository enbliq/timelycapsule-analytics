from fastapi import APIRouter, Depends, Body
from app.services.analytics_engine import AnalyticsProcessor
from app.schemas.analytics_schemas import SentimentRequest, SentimentResponse
from app.models.capsule import CapsuleContent
from app.core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/sentiment", tags=["Sentiment Analysis"])

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