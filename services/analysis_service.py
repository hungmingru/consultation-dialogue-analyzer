from pipeline.analysis.quality_scorer import score_quality
from pipeline.analysis.rules_engine import evaluate_rules
from pipeline.preprocess.cleaner import clean_text


def analyze_conversation(messages):
    cleaned = []
    for msg in messages:
        cleaned.append(
            {
                "sender_type": msg.get("sender_type"),
                "sender_id": msg.get("sender_id"),
                "content": clean_text(msg.get("content", "")),
                "timestamp": msg.get("timestamp"),
            }
        )

    rule_hits = evaluate_rules(cleaned)
    quality_score = score_quality(cleaned, rule_hits)

    sentiment_label = "neutral"
    risk_level = "low"
    if any(hit.get("severity") == "high" for hit in rule_hits):
        risk_level = "high"
    elif any(hit.get("severity") == "medium" for hit in rule_hits):
        risk_level = "medium"

    summary_text = "本次会话已完成基础分析。"
    if rule_hits:
        summary_text += " 检测到：" + "; ".join(hit.get("match_text", "") for hit in rule_hits[:3])
    else:
        summary_text += " 未检测到明显问题。"

    return {
        "quality_score": quality_score,
        "sentiment_label": sentiment_label,
        "risk_level": risk_level,
        "summary_text": summary_text,
        "rule_hits": rule_hits,
    }
