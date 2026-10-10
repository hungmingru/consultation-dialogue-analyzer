from sqlalchemy import text

from app.database import Base, engine


def init_db():
    Base.metadata.create_all(bind=engine)

    with engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS sensitive_words (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word TEXT,
                    category TEXT,
                    severity TEXT
                )
                """
            )
        )
        conn.execute(
            text(
                """
                INSERT OR IGNORE INTO sensitive_words (word, category, severity) VALUES
                ('投诉', 'complaint', 'high'),
                ('退款', 'refund', 'high'),
                ('不满意', 'negative', 'high'),
                ('威胁', 'threat', 'critical')
                """
            )
        )

        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS etiquette_words (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word TEXT,
                    category TEXT,
                    impact TEXT
                )
                """
            )
        )
        conn.execute(
            text(
                """
                INSERT OR IGNORE INTO etiquette_words (word, category, impact) VALUES
                ('您好', 'greeting', 'positive'),
                ('谢谢', 'gratitude', 'positive'),
                ('感谢', 'gratitude', 'positive'),
                ('请稍等', 'politeness', 'positive')
                """
            )
        )

    print("Database initialized.")
