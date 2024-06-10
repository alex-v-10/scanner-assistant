import sqlite3

def create_table():
    conn = sqlite3.connect('data.db')
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
    