from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_uuid = Column(String(64), unique=True, index=True, nullable=False)
    mobile = Column(String(32), nullable=True)
    nick_name = Column(String(255), nullable=True)
    source_channel = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)


class Consultant(Base):
    __tablename__ = "consultants"

    id = Column(Integer, primary_key=True, index=True)
    consultant_uuid = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    team_name = Column(String(255), nullable=True)
    role = Column(String(64), nullable=True)
    status = Column(String(32), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    conversation_uuid = Column(String(64), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    consultant_id = Column(Integer, ForeignKey("consultants.id"), nullable=True)
    source_channel = Column(String(64), nullable=True)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    total_turns = Column(Integer, default=0)
    user_message_count = Column(Integer, default=0)
    consultant_message_count = Column(Integer, default=0)
    status = Column(String(32), default="open")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    message_uuid = Column(String(64), unique=True, index=True, nullable=False)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    sender_type = Column(String(32), nullable=False)
    sender_id = Column(Integer, nullable=True)
    content = Column(Text, nullable=True)
    message_type = Column(String(32), default="text")
    timestamp = Column(DateTime, nullable=False)
    seq_no = Column(Integer, default=0)
    attachment_url = Column(String(512), nullable=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class ConversationAnalysis(Base):
    __tablename__ = "conversation_analysis"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    quality_score = Column(Float, default=0.0)
    sentiment_label = Column(String(32), default="neutral")
    sentiment_score = Column(Float, default=0.0)
    risk_level = Column(String(32), default="low")
    intent_label = Column(String(64), default="general_inquiry")
    summary_text = Column(Text, nullable=True)
    model_version = Column(String(64), nullable=True)
    analyzed_at = Column(DateTime, default=datetime.utcnow)


class RuleHit(Base):
    __tablename__ = "rule_hits"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    rule_name = Column(String(128), nullable=False)
    rule_category = Column(String(64), nullable=True)
    severity = Column(String(32), default="medium")
    match_text = Column(Text, nullable=True)
    matched_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)


class TopicLabel(Base):
    __tablename__ = "topic_labels"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    topic_name = Column(String(128), nullable=False)
    confidence_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)


class RiskEvent(Base):
    __tablename__ = "risk_events"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    risk_type = Column(String(64), nullable=False)
    risk_level = Column(String(32), default="medium")
    trigger_reason = Column(Text, nullable=True)
    detected_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
