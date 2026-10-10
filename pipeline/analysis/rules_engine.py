SENSITIVE_WORDS = [
    "投诉",
    "退款",
    "退费",
    "不满意",
    "辱骂",
    "严重",
    "违法",
    "威胁",
    "无法接受",
]

ETIQUETTE_WORDS = ["您好", "谢谢", "感谢", "请稍等", "抱歉", "好的", "对不起"]
NEGATIVE_PATTERNS = ["不满意", "投诉", "无法解决", "退款", "很差", "太慢", "拖延"]


def evaluate_rules(messages):
    hits = []
    text_all = "\n".join(msg.get("content", "") for msg in messages)

    for word in SENSITIVE_WORDS:
        if word in text_all:
            hits.append(
                {
                    "rule_name": "sensitive_word_detected",
                    "rule_category": "sensitive_word",
                    "severity": "high",
                    "match_text": word,
                }
            )

    for word in ETIQUETTE_WORDS:
        if word in text_all:
            hits.append(
                {
                    "rule_name": "etiquette_detected",
                    "rule_category": "etiquette",
                    "severity": "low",
                    "match_text": word,
                }
            )

    for msg in messages:
        content = msg.get("content", "")
        for pattern in NEGATIVE_PATTERNS:
            if pattern in content:
                hits.append(
                    {
                        "rule_name": "negative_pattern_detected",
                        "rule_category": "complaint",
                        "severity": "medium",
                        "match_text": pattern,
                    }
                )
                break

    return hits
