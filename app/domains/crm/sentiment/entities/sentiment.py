# domains/crm/sentiment/entities/sentiment.py
from datetime import datetime
from typing import Optional
from enum import Enum

class SentimentType(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    COMPLAINT = "complaint"
    SUGGESTION = "suggestion"

class SentimentEntity:
    def __init__(
        self,
        id: Optional[int] = None,
        customer_id: Optional[int] = None,
        sentiment_type: SentimentType = SentimentType.NEUTRAL,
        comments: str = "",
        rating: Optional[int] = None,  # 1-5 scale
        is_resolved: bool = False,
        resolved_notes: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.customer_id = customer_id
        self.sentiment_type = sentiment_type
        self.comments = comments
        self.rating = rating
        self.is_resolved = is_resolved
        self.resolved_notes = resolved_notes
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()