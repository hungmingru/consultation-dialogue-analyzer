import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = "consultation-dialogue-analyzer"
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/app.db")
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
