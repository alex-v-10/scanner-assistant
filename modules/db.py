import sqlite3
import traceback
from .const import DATABASE

def create_table():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS telegram_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                channel TEXT,
                project TEXT,
                messages TEXT,
                messages_count TEXT,
                chatbot_answer TEXT,
                answer_search TEXT,
                messages_search TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS telegram_last_ids (
                channel TEXT PRIMARY KEY,
                last_id TEXT
            )
        ''')
        conn.commit()
    except Exception as e:
        traceback.print_exc() 
        print(f"An unexpected error occurred: {e}")
    finally:
        cursor.close()
        conn.close()
