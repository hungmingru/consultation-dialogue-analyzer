from typing import List

from fastapi import FastAPI
from pydantic import BaseModel

from app.database import Base, engine
from services.analysis_service import analyze_conversation

app = FastAPI(title="Consultation Dialogue Analyzer")


class MessageInput(BaseModel):
    conversation_id: int
    sender_type: str
    sender_id: int | None = None
    content: str
    message_type: str = "text"
    timestamp: str


@app.on_event("startup")
def startup_event() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/analyze")
def analyze_api(messages: List[MessageInput]):
    payload = [
        {
            "conversation_id": item.conversation_id,
            "sender_type": item.sender_type,
            "sender_id": item.sender_id,
            "content": item.content,
            "message_type": item.message_type,
            "timestamp": item.timestamp,
        }
        for item in messages
    ]
    return analyze_conversation(payload)
