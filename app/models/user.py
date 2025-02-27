from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class UserActivity(Base):
    __tablename__ = "user_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    capsule_id = Column(Integer, index=True)
    activity_type = Column(String(50), index=True)
    activity_details = Column(JSON)
    timestamp = Column(DateTime, server_default=func.now())

class UserAnalyticsProfile(Base):
    __tablename__ = "user_analytics_profiles"
    
    user_id = Column(Integer, primary_key=True, index=True)
    engagement_score = Column(Integer, default=0)
    last_activity = Column(DateTime)
    favorite_capsule_type = Column(String(100))
    sentiment_trend = Column(JSON)