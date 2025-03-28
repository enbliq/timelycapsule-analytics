from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np
from wordcloud import WordCloud
import base64
from io import BytesIO
from typing import List

class AnalyticsProcessor:
    FLAGGED_WORDS = [
        'hate', 'violence', 'profanity', 'racist', 'attack'  # Add more words
    ]
    @staticmethod
    def analyze_sentiment(text: str) -> dict:
        analysis = TextBlob(text)
        return {
            "polarity": round(analysis.sentiment.polarity, 3),
            "subjectivity": round(analysis.sentiment.subjectivity, 3),
            "assessment": "positive" if analysis.sentiment.polarity > 0 else "negative"
        }
    
    @staticmethod
    def calculate_document_similarity(source_doc: str, target_docs: List[str]):
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform([source_doc] + target_docs)
        cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
        return np.argsort(cosine_similarities)[::-1].tolist()
    
    @staticmethod
    def generate_temporal_trends(contents: List[str], timestamps: List[datetime]):
        # Implement time-based topic tracking
        pass  # Add implementation using NLTK's time-aware analysis

    @staticmethod
    def detect_topic_clusters(texts: List[str], num_clusters=5):
        # Implement K-means clustering for topic discovery
        pass  # Add scikit-learn clustering implementation
    
    @staticmethod
    def generate_wordcloud(text_corpus: str) -> str:
        wc = WordCloud(width=800, height=400).generate(text_corpus)
        img = BytesIO()
        wc.to_image().save(img, format='PNG')
        return base64.b64encode(img.getvalue()).decode('utf-8')

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
    
   

    @staticmethod
    def analyze_moderation_score(text: str) -> dict:
        # Preprocess text and find flagged words
        text_clean = re.sub(r'[^\w\s]', '', text.lower())
        found_words = [word for word in text_clean.split() if word in AnalyticsProcessor.FLAGGED_WORDS]
        
        # Calculate sentiment
        sentiment = AnalyticsProcessor.analyze_sentiment(text)
        
        # Calculate toxicity score (0-100)
        keyword_score = min(len(found_words) * 25, 60)  # Max 60 from keywords
        sentiment_score = max(0, -sentiment['polarity']) * 40  # Max 40 from sentiment
        toxicity_score = min(round(keyword_score + sentiment_score), 100)
        
        # Determine status
        if toxicity_score <= 30:
            status = "safe"
        elif toxicity_score <= 70:
            status = "needs review"
        else:
            status = "high-risk"
        
        return {
            "toxicity_score": toxicity_score,
            "flagged_words": list(set(found_words)),  # Deduplicate
            "status": status,
            "warning": "This message may violate community guidelines." if status != "safe" else None
        }