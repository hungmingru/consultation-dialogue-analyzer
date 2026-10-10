# Consultation Dialogue Analyzer

An open-source system to analyze consultation conversations from chat records and identify quality issues, sentiment, risks, and trend patterns.

## Features

- Chat record import from CSV/JSON
- Conversation reconstruction and cleaning
- Rule-based quality scoring
- Risk detection and alerts
- Basic API for analysis
- Report generation
- Dashboard support

## Project structure

- `app/`: FastAPI application and database models
- `pipeline/`: preprocessing and analysis logic
- `services/`: business services
- `scripts/`: import and analysis scripts
- `data/`: sample data and report outputs

## Quick start

1. Create a virtual environment

   python -m venv .venv
   source .venv/bin/activate

2. Install dependencies

   pip install -r requirements.txt

3. Initialize the database

   python scripts/init_db.py

4. Import sample data

   python scripts/import_wechat_data.py --file data/samples/sample_conversations.csv --type csv

5. Run analysis

   python scripts/batch_analyze.py

6. Start the API

   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

7. Open the API docs

   http://localhost:8000/docs

## Sample API call

POST /api/analyze

[
  {
    "conversation_id": 1,
    "sender_type": "user",
    "sender_id": 101,
    "content": "我很不满意，退款也没处理好",
    "timestamp": "2024-01-15T09:00:00",
    "message_type": "text"
  },
  {
    "conversation_id": 1,
    "sender_type": "consultant",
    "sender_id": 1,
    "content": "您好，非常抱歉，您可以提供订单号吗？",
    "timestamp": "2024-01-15T09:05:00",
    "message_type": "text"
  }
]

## Notes

This project is designed for a practical MVP using open-source Python tooling and is intended to be extended with more advanced NLP models over time.
