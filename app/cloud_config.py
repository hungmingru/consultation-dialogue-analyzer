"""
API Configuration for cloud sync service.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Cloud API Configuration
CLOUD_API_URL = os.getenv("CLOUD_API_URL", "https://api.example.com")
CLOUD_API_KEY = os.getenv("CLOUD_API_KEY", "your_api_key")
CLOUD_API_SECRET = os.getenv("CLOUD_API_SECRET", "your_api_secret")

# Sync Configuration
SYNC_BATCH_SIZE = int(os.getenv("SYNC_BATCH_SIZE", "100"))
SYNC_TIMEOUT = int(os.getenv("SYNC_TIMEOUT", "30"))  # seconds
SYNC_CURSOR_FILE = os.getenv("SYNC_CURSOR_FILE", "data/.sync_cursor")

# Notification Configuration
NOTIFY_ENABLE = os.getenv("NOTIFY_ENABLE", "true").lower() == "true"
WECHAT_WEBHOOK = os.getenv("WECHAT_WEBHOOK", "")
DINGTALK_WEBHOOK = os.getenv("DINGTALK_WEBHOOK", "")
FEISHU_WEBHOOK = os.getenv("FEISHU_WEBHOOK", "")

# LLM Configuration
LLM_ENABLE = os.getenv("LLM_ENABLE", "false").lower() == "true"
LLM_API_URL = os.getenv("LLM_API_URL", "https://api.openai.com/v1")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
