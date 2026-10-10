from datetime import datetime
from typing import Any, Dict, List


def build_conversation(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    ordered = sorted(messages, key=lambda x: x.get("timestamp") or datetime.min)
    result = []
    for idx, msg in enumerate(ordered, start=1):
        result.append(
            {
                "seq_no": idx,
                "conversation_id": msg.get("conversation_id"),
                "sender_type": msg.get("sender_type"),
                "sender_id": msg.get("sender_id"),
                "content": msg.get("content", ""),
                "timestamp": msg.get("timestamp"),
                "message_type": msg.get("message_type", "text"),
            }
        )
    return result
