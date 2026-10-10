from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class MessageIn(BaseModel):
    conversation_id: int
    sender_type: str
    sender_id: Optional[int] = None
    content: str
    message_type: str = "text"
    timestamp: str


class AnalysisResultOut(BaseModel):
    conversation_id: int
    quality_score: float
    sentiment_label: str
    risk_level: str
    summary_text: Optional[str] = None
    analyzed_at: datetime
