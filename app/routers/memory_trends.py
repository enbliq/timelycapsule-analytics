from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.analytics_engine import AnalyticsProcessor
from app.models.capsule import CapsuleContent
from app.core.database import get_db
from sqlalchemy import select
import re
from collections import Counter
from typing import List
from pydantic import BaseModel

router = APIRouter(prefix="/memory-trends", tags=["Memory Trends"])

class TrendAnalysisResponse(BaseModel):
    top_words: List[dict]
    wordcloud: str
    trending_topics: List[str]
    timeframe: str

async def get_all_capsule_content(db: AsyncSession, timeframe_days: int = 30):
    result = await db.execute(
        select(CapsuleContent.content, CapsuleContent.created_at)
        .where(CapsuleContent.created_at >= func.now() - text(f"interval '{timeframe_days} days'"))
    )
    return result.all()

@router.get("/analyze", response_model=TrendAnalysisResponse)
async def analyze_memory_trends(
    timeframe_days: int = 30,
    max_words: int = 50,
    db: AsyncSession = Depends(get_db)
):
    try:
        # Get content from database
        content_records = await get_all_capsule_content(db, timeframe_days)
        
        # Text processing
        all_text = " ".join([record[0] for record in content_records]).lower()
        words = re.findall(r'\b[a-z]{3,}\b', all_text)
        
        # Filter stopwords and count
        with open("stopwords.txt") as f:
            stopwords = set(f.read().splitlines())
            
        filtered_words = [word for word in words if word not in stopwords]
        word_counts = Counter(filtered_words).most_common(max_words)
        
        # Generate word cloud
        wordcloud = AnalyticsProcessor.generate_wordcloud(" ".join(filtered_words))
        
        # Extract trending topics using TF-IDF
        documents = [record[0] for record in content_records]
        trending_topics = AnalyticsProcessor.generate_tfidf_recommendations(documents)
        
        return {
            "top_words": [{"word": w, "count": c} for w, c in word_counts],
            "wordcloud": wordcloud,
            "trending_topics": trending_topics,
            "timeframe": f"{timeframe_days} days"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))