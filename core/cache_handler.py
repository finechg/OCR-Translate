

import sqlite3
from pathlib import Path
import os

class TranslationCacheManager:
    def __init__(self, base_dir="cache", base_name="translation_cache", max_items=1_000_000):
        self.base_dir = Path(base_dir)
        self.base_name = base_name
        self.max_items = max_items
        self.db_paths = self.load_db_list()
        self.connections = {path: sqlite3.connect(path) for path in self.db_paths}
        for conn in self.connections.values():
            self._initialize_db(conn)

    def _initialize_db(self, conn):
        conn.execute(
            "CREATE TABLE IF NOT EXISTS cache (key TEXT PRIMARY KEY, value TEXT)"
        )
        conn.commit()

    def load_db_list(self):
        db_files = sorted(self.base_dir.glob(f"{self.base_name}*.db"))
        if not db_files:
            default_path = self.base_dir / f"{self.base_name}00.db"
            default_path.touch()
            return [default_path]
        return db_files

    def get_total_items(self):
        total = 0
        for conn in self.connections.values():
            cursor = conn.execute("SELECT COUNT(*) FROM cache")
            total += cursor.fetchone()[0]
        return total

    def detect_db_for_insert(self):
        for path, conn in self.connections.items():
            cursor = conn.execute("SELECT COUNT(*) FROM cache")
            if cursor.fetchone()[0] < self.max_items:
                return path, conn

        index = len(self.connections)
        new_db_path = self.base_dir / f"{self.base_name}{index:02d}.db"
        new_conn = sqlite3.connect(new_db_path)
        self._initialize_db(new_conn)
        self.connections[new_db_path] = new_conn
        return new_db_path, new_conn

    def add_entry(self, key, value):
        path, conn = self.detect_db_for_insert()
        try:
            conn.execute("INSERT OR REPLACE INTO cache (key, value) VALUES (?, ?)", (key, value))
            conn.commit()
        except Exception as e:
            print(f"Insert error in {path.name}: {e}")

    def get_entry(self, key):
        for path, conn in self.connections.items():
            cursor = conn.execute("SELECT value FROM cache WHERE key=?", (key,))
            row = cursor.fetchone()
            if row:
                return row[0]
        return None

    def close_all(self):
        for conn in self.connections.values():
            conn.close()