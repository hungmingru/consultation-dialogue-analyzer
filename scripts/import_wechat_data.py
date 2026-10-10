import argparse
import csv
import json
import os
import sys
import uuid
from datetime import datetime

from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine, Base
from app.models import Conversation, Message, User, Consultant

Session = sessionmaker(bind=engine)


class WeChatImporter:
    def __init__(self):
        self.session = Session()
        self.user_cache = {}
        self.consultant_cache = {}

    def get_or_create_user(self, user_id: str, nick_name: str = None):
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
        if consultant_id in self.consultant_cache:
            return self.consultant_cache[consultant_id]

        consultant = self.session.query(Consultant).filter(Consultant.consultant_uuid == consultant_id).first()
        if consultant:
            self.consultant_cache[consultant_id] = consultant.id
            return consultant.id

        new_consultant = Consultant(consultant_uuid=consultant_id, name=name or consultant_id, team_name="客服")
        self.session.add(new_consultant)
        self.session.flush()
        self.consultant_cache[consultant_id] = new_consultant.id
        return new_consultant.id

    def import_csv(self, csv_path: str):
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        for row in rows:
            conv_id = str(row["conversation_id"])
            sender_type = str(row["sender_type"]).lower()
            sender_id = str(row["sender_id"])
            sender_name = row.get("sender_name") or sender_id
            content = row.get("content", "").strip()
            ts_raw = row.get("timestamp")
            ts = self._parse_ts(ts_raw)

            if not content:
                continue

            conversation = self.session.query(Conversation).filter(Conversation.conversation_uuid == conv_id).first()
            if not conversation:
                conversation = Conversation(conversation_uuid=conv_id, source_channel="wechat", status="closed")
                self.session.add(conversation)
                self.session.flush()

            if sender_type == "user":
                user_id = self.get_or_create_user(sender_id, sender_name)
                conversation.user_id = user_id
            elif sender_type == "consultant":
                consultant_id = self.get_or_create_consultant(sender_id, sender_name)
                conversation.consultant_id = consultant_id

            message = Message(
                message_uuid=str(uuid.uuid4()),
                conversation_id=conversation.id,
                sender_type=sender_type,
                sender_id=self.get_or_create_user(sender_id, sender_name) if sender_type == "user" else self.get_or_create_consultant(sender_id, sender_name),
                content=content,
                message_type=row.get("message_type", "text"),
                timestamp=ts,
            )
            self.session.add(message)

        self.session.commit()
        return len(rows)

    def _parse_ts(self, ts_raw):
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


def main():
    parser = argparse.ArgumentParser(description="Import chat records into the database")
    parser.add_argument("--file", required=True)
    parser.add_argument("--type", choices=["csv", "json"], default="csv")
    args = parser.parse_args()

    Base.metadata.create_all(bind=engine)
    importer = WeChatImporter()

    if args.type == "csv":
        count = importer.import_csv(args.file)
        print(f"Imported {count} messages from CSV")
    else:
        with open(args.file, encoding="utf-8") as f:
            data = json.load(f)
        records = data.get("records", data)
        for rec in records:
            rec["conversation_id"] = rec["conversation_id"]
        # For JSON we use CSV-compatible conversion
        temp_path = os.path.join(os.path.dirname(args.file), "__tmp_import.csv")
        with open(temp_path, "w", newline="", encoding="utf-8") as out:
            writer = csv.DictWriter(out, fieldnames=["conversation_id", "sender_type", "sender_id", "sender_name", "content", "timestamp", "message_type"])
            writer.writeheader()
            for rec in records:
                writer.writerow({
                    "conversation_id": rec.get("conversation_id"),
                    "sender_type": rec.get("sender_type", "user"),
                    "sender_id": rec.get("sender_id", ""),
                    "sender_name": rec.get("sender_name", ""),
                    "content": rec.get("content", ""),
                    "timestamp": rec.get("timestamp", datetime.utcnow().isoformat()),
                    "message_type": rec.get("message_type", "text")
                })
        count = importer.import_csv(temp_path)
        os.remove(temp_path)
        print(f"Imported {count} messages from JSON")


if __name__ == "__main__":
    main()
