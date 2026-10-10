import os
import sys
from datetime import datetime

from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine
from app.models import Conversation, Message, ConversationAnalysis, RuleHit
from pipeline.analysis.quality_scorer import score_quality
from pipeline.analysis.rules_engine import evaluate_rules
from pipeline.preprocess.cleaner import clean_text

Session = sessionmaker(bind=engine)


def get_all_conversations():
    session = Session()
    conversations = session.query(Conversation).all()
    session.close()
    return conversations


def analyze_conversation(conversation_id):
    session = Session()
    messages = session.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.timestamp.asc()).all()
    payload = [{
        "sender_type": msg.sender_type,
        "sender_id": msg.sender_id,
        "content": clean_text(msg.content or ""),
        "timestamp": msg.timestamp,
    } for msg in messages]

    rule_hits = evaluate_rules(payload)
    quality_score = score_quality(payload, rule_hits)

    risk_level = "low"
    if any(hit.get("severity") == "high" for hit in rule_hits):
        risk_level = "high"
    elif any(hit.get("severity") == "medium" for hit in rule_hits):
        risk_level = "medium"

    summary_text = "本次会话已完成基础分析。"
    if rule_hits:
        summary_text += " 检测到：" + "; ".join(hit.get("match_text") for hit in rule_hits[:3])
    else:
        summary_text += " 未检测到明显问题。"

    existing = session.query(ConversationAnalysis).filter(ConversationAnalysis.conversation_id == conversation_id).first()
    if existing:
        existing.quality_score = quality_score
        existing.sentiment_label = "neutral"
        existing.risk_level = risk_level
        existing.summary_text = summary_text
        existing.analyzed_at = datetime.utcnow()
    else:
        session.add(ConversationAnalysis(
            conversation_id=conversation_id,
            quality_score=quality_score,
            sentiment_label="neutral",
            risk_level=risk_level,
            summary_text=summary_text,
            analyzed_at=datetime.utcnow(),
        ))

    session.query(RuleHit).filter(RuleHit.conversation_id == conversation_id).delete()
    for hit in rule_hits:
        session.add(RuleHit(
            conversation_id=conversation_id,
            rule_name=hit.get("rule_name", "unknown"),
            rule_category=hit.get("rule_category", "unknown"),
            severity=hit.get("severity", "medium"),
            match_text=hit.get("match_text", ""),
            matched_at=datetime.utcnow(),
        ))

    session.commit()
    session.close()
    print(f"Analyzed conversation {conversation_id}: score={quality_score}, risk={risk_level}")


def main():
    for conv in get_all_conversations():
        analyze_conversation(conv.id)

    print("All conversations analyzed.")


if __name__ == "__main__":
    main()
