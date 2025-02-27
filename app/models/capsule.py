from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class CapsuleContent(Base):
    __tablename__ = "capsule_contents"
    
    id = Column(Integer, primary_key=True, index=True)
    original_capsule_id = Column(Integer, index=True)
    title = Column(String(255))
    content = Column(Text)
    media_metadata = Column(JSON)
    sentiment_score = Column(Float)
    created_at = Column(DateTime)
    unlocked_at = Column(DateTime)
    owner_id = Column(Integer, index=True)
    tags = Column(JSON)