from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import pandas as pd
import numpy as np

class AnalyticsProcessor:
    @staticmethod
    def analyze_sentiment(text: str) -> dict:
        analysis = TextBlob(text)
        return {
            "polarity": round(analysis.sentiment.polarity, 3),
            "subjectivity": round(analysis.sentiment.subjectivity, 3),
            "assessment": "positive" if analysis.sentiment.polarity > 0 else "negative"
        }

    @staticmethod
    def generate_tfidf_recommendations(documents: list[str]) -> list:
        vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 3),
            max_features=5000
        )
        tfidf_matrix = vectorizer.fit_transform(documents)
        feature_names = vectorizer.get_feature_names_out()
        
        # Calculate document similarity
        cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
        np.fill_diagonal(cosine_sim, 0)  # Exclude self-similarity
        sim_scores = cosine_sim.mean(axis=0)
        
        top_indices = sim_scores.argsort()[-5:][::-1]
        return [feature_names[idx] for idx in top_indices]

    @staticmethod
    def process_temporal_analysis(activities: pd.DataFrame) -> dict:
        # Advanced temporal analysis
        activities['timestamp'] = pd.to_datetime(activities['timestamp'])
        return {
            "hourly_engagement": activities.resample('H', on='timestamp').size().to_dict(),
            "daily_trends": activities.groupby([pd.Grouper(key='timestamp', freq='D'), 'activity_type']).size().unstack(fill_value=0).to_dict(),
            "weekly_correlation": activities.groupby([activities['timestamp'].dt.day_name(), 'activity_type']).size().unstack(fill_value=0).to_dict()
        }