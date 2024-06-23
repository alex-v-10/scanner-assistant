import sqlite3
import traceback
from .const import DATABASE

def create_table():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS telegram (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                channel TEXT,
                project TEXT,
                messages TEXT,
                messages_count TEXT,
                chatbot_answer TEXT,
                answer_search TEXT,
                messages_search TEXT,
                UNIQUE (date, channel)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS telegram_min_ids (
                channel TEXT PRIMARY KEY,
                min_id TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ignore_list (
                date TEXT PRIMARY KEY,
                telegram_channels TEXT,
                youtube TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS charts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                project TEXT,
                telegram TEXT,
                youtube TEXT,
                youtube_approx TEXT,
                UNIQUE(date, project)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS youtube (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                project TEXT,
                keyword TEXT,
                videos TEXT,
                videos_approx TEXT,
                popular TEXT,
                UNIQUE(date, project, keyword)
            )
        ''')

        conn.commit()
    except Exception as e:
        traceback.print_exc() 
        print(f"An unexpected error occurred: {e}")
    finally:
        cursor.close()
        conn.close()
