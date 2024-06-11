import sqlite3
from .const import DATABASE

def create_table():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS telegram_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            channel TEXT,
            project TEXT,
            messages TEXT,
            messages_count TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS telegram_last_ids (
            channel TEXT PRIMARY KEY,
            last_id TEXT
        )
    ''')
    conn.commit()
    conn.close()
    