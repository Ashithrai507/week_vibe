import sqlite3
import time
from storage.app_paths import get_app_data_dir

DB_NAME = "chat.db"


class ChatDB:
    def __init__(self):
        app_dir = get_app_data_dir()
        db_path = app_dir / DB_NAME

        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_table()

    def create_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                peer_ip TEXT,
                direction TEXT,
                message TEXT,
                timestamp REAL
            )
        """)
        self.conn.commit()

    def save_message(self, peer_ip, direction, message):
        self.conn.execute(
            "INSERT INTO messages (peer_ip, direction, message, timestamp) VALUES (?, ?, ?, ?)",
            (peer_ip, direction, message, time.time())
        )
        self.conn.commit()

    def load_messages(self, peer_ip):
        cursor = self.conn.execute(
            "SELECT direction, message FROM messages WHERE peer_ip=? ORDER BY id",
            (peer_ip,)
        )
        return cursor.fetchall()
