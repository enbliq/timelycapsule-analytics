# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.database import engine, Base
from app.routers import (
    engagement,
    sentiment,
    memory_trends,
    recommendations,
    dashboard
)
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialized")
    
    yield
    
    # Cleanup
    await engine.dispose()
    logger.info("Database connection closed")

app = FastAPI(
    title="TimelyCapsule Analytics API",
    description="AI-powered analytics service for time capsule platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(engagement.router)
app.include_router(sentiment.router)
app.include_router(memory_trends.router)
app.include_router(recommendations.router)
app.include_router(dashboard.router)

@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "database": "connected" if not engine.is_closed() else "disconnected",
            "analytics_engine": "operational"
        }
    }

@app.get("/", tags=["System"])
async def root():
    return {
        "message": "TimelyCapsule Analytics Service",
        "endpoints": {
            "engagement": "/engagement",
            "sentiment": "/sentiment",
            "memory_trends": "/memory-trends",
            "recommendations": "/recommendations",
            "dashboard": "/dashboard"
        }
    }