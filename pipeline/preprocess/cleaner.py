import re

import jieba


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.strip()
    text = text.replace("\u200b", "")
    text = re.sub(r"\s+", "", text)
    text = re.sub(r"[\x00-\x1F\x7F]+", "", text)
    return text


def tokenize(text: str):
    text = clean_text(text)
    return [word for word in jieba.cut(text) if word.strip()]
