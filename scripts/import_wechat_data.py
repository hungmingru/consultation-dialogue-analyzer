"""
Improved WeChat data importer with cloud API support.
"""

import argparse
import csv
import json
import os
import sys
import uuid
from datetime import datetime
from typing import List, Dict, Any

from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, Base
from app.models import Conversation, Message, User, Consultant
from app.cloud_api_client import CloudAPIClient

Session = sessionmaker(bind=engine)


class WeChatImporter:
    def __init__(self):
        self.session = Session()
        self.user_cache = {}
        self.consultant_cache = {}
        self.import_count = 0
        self.skip_count = 0

    def get_or_create_user(self, user_id: str, nick_name: str = None):
        """Get or create user by ID."""
        if user_id in self.user_cache:
            return self.user_cache[user_id]

        user = self.session.query(User).filter(User.user_uuid == user_id).first()
        if user:
            self.user_cache[user_id] = user.id
            return user.id

        new_user = User(user_uuid=user_id, nick_name=nick_name or user_id, source_channel="wechat")
        self.session.add(new_user)
        self.session.flush()
        self.user_cache[user_id] = new_user.id
        return new_user.id

    def get_or_create_consultant(self, consultant_id: str, name: str = None):
        """Get or create consultant by ID."""
        if consultant_id in self.consultant_cache:
            return self.consultant_cache[consultant_id]

        consultant = self.session.query(Consultant).filter(
            Consultant.consultant_uuid == consultant_id
        ).first()
        if consultant:
            self.consultant_cache[consultant_id] = consultant.id
            return consultant.id

        new_consultant = Consultant(
            consultant_uuid=consultant_id,
            name=name or consultant_id,
            team_name="客服"
        )
        self.session.add(new_consultant)
        self.session.flush()
        self.consultant_cache[consultant_id] = new_consultant.id
        return new_consultant.id

    def _parse_timestamp(self, ts_raw: str) -> datetime:
        """Parse timestamp from various formats."""
        if not ts_raw:
            return datetime.utcnow()
        
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S%z"):
            try:
                return datetime.strptime(ts_raw, fmt)
            except ValueError:
                pass
        
        try:
            return datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
        except Exception:
            return datetime.utcnow()

    def _should_skip_message(self, conversation_uuid: str, message_uuid: str) -> bool:
        """Check if message already exists to avoid duplicates."""
        if not message_uuid:
            return True
        
        existing = self.session.query(Message).filter(
            Message.message_uuid == message_uuid
        ).first()
        return existing is not None

    def import_from_cloud_api(self, max_batches: int = None):
        """Import conversations from cloud API with incremental cursor."""
        print("\n" + "="*60)
        print("📡 Importing from Cloud API...")
        print("="*60)
        
        client = CloudAPIClient()
        conversations_data = client.fetch_all_conversations(max_batches=max_batches)
        
        self._import_conversations(conversations_data)
        return self.import_count

    def import_from_csv(self, csv_path: str):
        """Import conversations from CSV file."""
        print(f"\n" + "="*60)
        print(f"📄 Importing from CSV: {csv_path}")
        print("="*60)
        
        conversations_data = []
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                conversations_data.append({
                    "conversation_id": row.get("conversation_id"),
                    "message_id": row.get("message_id", str(uuid.uuid4())),
                    "sender_type": row.get("sender_type", "user").lower(),
                    "sender_id": row.get("sender_id"),
                    "sender_name": row.get("sender_name", row.get("sender_id", "")),
                    "content": row.get("content", ""),
                    "timestamp": row.get("timestamp"),
                    "message_type": row.get("message_type", "text")
                })
        
        self._import_conversations(conversations_data)
        return self.import_count

    def import_from_json(self, json_path: str):
        """Import conversations from JSON file."""
        print(f"\n" + "="*60)
        print(f"📄 Importing from JSON: {json_path}")
        print("="*60)
        
        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)
        
        conversations_data = data.get("records", data if isinstance(data, list) else [])
        self._import_conversations(conversations_data)
        return self.import_count

    def _import_conversations(self, conversations_data: List[Dict[str, Any]]):
        """Import a list of conversation records."""
        conversations_map = {}  # conv_id -> Conversation object
        
        for record in conversations_data:
            conv_id = str(record.get("conversation_id", ""))
            message_id = record.get("message_id", str(uuid.uuid4()))
            sender_type = str(record.get("sender_type", "user")).lower()
            sender_id = str(record.get("sender_id", ""))
            sender_name = record.get("sender_name", sender_id)
            content = record.get("content", "").strip()
            ts_raw = record.get("timestamp")
            ts = self._parse_timestamp(ts_raw)
            msg_type = record.get("message_type", "text")

            # Skip empty messages
            if not content or not conv_id:
                self.skip_count += 1
                continue

            # Skip if message already exists
            if self._should_skip_message(conv_id, message_id):
                self.skip_count += 1
                continue

            # Get or create conversation
            if conv_id not in conversations_map:
                conversation = self.session.query(Conversation).filter(
                    Conversation.conversation_uuid == conv_id
                ).first()
                if not conversation:
                    conversation = Conversation(
                        conversation_uuid=conv_id,
                        source_channel="wechat",
                        status="closed"
                    )
                    self.session.add(conversation)
                    self.session.flush()
                conversations_map[conv_id] = conversation
            else:
                conversation = conversations_map[conv_id]

            # Associate user/consultant with conversation
            if sender_type == "user":
                user_id = self.get_or_create_user(sender_id, sender_name)
                if not conversation.user_id:
                    conversation.user_id = user_id
            elif sender_type == "consultant":
                consultant_id = self.get_or_create_consultant(sender_id, sender_name)
                if not conversation.consultant_id:
                    conversation.consultant_id = consultant_id

            # Add message
            message = Message(
                message_uuid=message_id,
                conversation_id=conversation.id,
                sender_type=sender_type,
                sender_id=(
                    self.get_or_create_user(sender_id, sender_name)
                    if sender_type == "user"
                    else self.get_or_create_consultant(sender_id, sender_name)
                ),
                content=content,
                message_type=msg_type,
                timestamp=ts,
            )
            self.session.add(message)
            self.import_count += 1

        # Update conversation statistics
        self._update_conversation_stats(conversations_map.values())
        
        self.session.commit()
        print(f"\n✓ Import complete: {self.import_count} messages, {self.skip_count} skipped")

    def _update_conversation_stats(self, conversations):
        """Update conversation statistics."""
        for conv in conversations:
            messages = self.session.query(Message).filter(
                Message.conversation_id == conv.id,
                Message.is_deleted == False
            ).all()

            if not messages:
                continue

            messages = sorted(messages, key=lambda m: m.timestamp or datetime.min)
            conv.total_turns = len(messages)
            conv.start_time = messages[0].timestamp
            conv.end_time = messages[-1].timestamp
            conv.user_message_count = len([m for m in messages if m.sender_type == "user"])
            conv.consultant_message_count = len([m for m in messages if m.sender_type == "consultant"])

            # Update message seq_no
            for idx, msg in enumerate(messages, start=1):
                msg.seq_no = idx

    def close(self):
        """Close database session."""
        self.session.close()


def main():
    parser = argparse.ArgumentParser(description="Import chat records from various sources")
    parser.add_argument(
        "--source",
        choices=["cloud", "csv", "json"],
        default="cloud",
        help="Data source: cloud API, CSV file, or JSON file"
    )
    parser.add_argument("--file", type=str, help="File path for CSV or JSON import")
    parser.add_argument(
        "--max-batches",
        type=int,
        help="Max batches to fetch from cloud API (for testing)"
    )
    
    args = parser.parse_args()

    Base.metadata.create_all(bind=engine)
    importer = WeChatImporter()

    try:
        if args.source == "cloud":
            count = importer.import_from_cloud_api(max_batches=args.max_batches)
        elif args.source == "csv":
            if not args.file:
                print("Error: --file is required for CSV import")
                return
            count = importer.import_from_csv(args.file)
        elif args.source == "json":
            if not args.file:
                print("Error: --file is required for JSON import")
                return
            count = importer.import_from_json(args.file)
        
        print(f"\n✓ Successfully imported {count} messages")
    except Exception as e:
        print(f"✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        importer.close()


if __name__ == "__main__":
    main()
