from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.analytics_engine import AnalyticsProcessor
from app.models.capsule import CapsuleContent
from app.core.database import get_db
from sqlalchemy import select
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

class RecommendationResponse(BaseModel):
    user_id: int
    recommended_themes: List[str]
    similar_capsules: List[int]
    trending_topics: List[str]

async def get_user_content(user_id: int, db: AsyncSession):
    result = await db.execute(
        select(CapsuleContent.content)
        .where(CapsuleContent.owner_id == user_id)
    )
    return [row[0] for row in result.all()]

@router.get("/for-user/{user_id}", response_model=RecommendationResponse)
async def get_personalized_recommendations(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    try:
        # Get user's historical content
        user_content = await get_user_content(user_id, db)
        
        # Get all content for trending analysis
        all_content_result = await db.execute(select(CapsuleContent.content))
        all_content = [row[0] for row in all_content_result.all()]
        
        if not user_content:
            # Fallback to general recommendations
            recommendations = AnalyticsProcessor.generate_tfidf_recommendations(all_content)
            return {
                "user_id": user_id,
                "recommended_themes": recommendations,
                "similar_capsules": [],
                "trending_topics": recommendations[:3]
            }
        
        # Personalized recommendations
        user_recommendations = AnalyticsProcessor.generate_tfidf_recommendations(user_content)
        
        # Find similar capsules
        all_docs = [" ".join([content for content in all_content])]
        user_profile = " ".join(user_content)
        similarity_scores = AnalyticsProcessor.calculate_document_similarity(user_profile, all_docs)
        
        return {
            "user_id": user_id,
            "recommended_themes": user_recommendations,
            "similar_capsules": similarity_scores[:5],
            "trending_topics": AnalyticsProcessor.generate_tfidf_recommendations(all_content)[:3]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))