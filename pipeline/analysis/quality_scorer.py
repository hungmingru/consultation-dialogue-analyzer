def score_quality(messages, rule_hits):
    score = 100.0

    for hit in rule_hits:
        severity = hit.get("severity", "medium")
        if severity == "high":
            score -= 18
        elif severity == "medium":
            score -= 10
        else:
            score -= 3

    total_chars = sum(len((msg.get("content") or "")) for msg in messages)
    if total_chars > 5000:
        score -= 8

    short_reply_count = 0
    for msg in messages:
        content = (msg.get("content") or "").strip()
        if msg.get("sender_type") == "consultant" and 0 < len(content) < 8:
            short_reply_count += 1

    score -= short_reply_count * 5
    score = max(0.0, min(score, 100.0))
    return round(score, 2)
