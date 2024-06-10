import sqlite3

def create_table():
    conn = sqlite3.connect('info.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS telegram_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel TEXT,
            project TEXT,
            date TEXT,
            messages TEXT
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
    