import sqlite3
from pathlib import Path

class RewriteCacheManager:
    def __init__(self, db_path="cache/rewrite_cache_gpt4mini.db"):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(self.db_path)
        self._initialize()

    def _initialize(self):
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS cache (key TEXT PRIMARY KEY, value TEXT)"
        )
        self.conn.commit()

    def get(self, key):
        cursor = self.conn.execute("SELECT value FROM cache WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row[0] if row else None

    def add(self, key, value):
        self.conn.execute(
            "INSERT OR REPLACE INTO cache (key, value) VALUES (?, ?)", (key, value)
        )
        self.conn.commit()

    def close(self):
        self.conn.close()