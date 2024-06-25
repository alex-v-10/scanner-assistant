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
                messages_count INTEGER,
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
                youtube TEXT,
                coingecko TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS charts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                project TEXT,
                telegram INTEGER,
                UNIQUE(date, project)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS youtube (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                project TEXT,
                keyword TEXT,
                videos INTEGER,
                videos_approx INTEGER,
                popular TEXT,
                UNIQUE(date, project, keyword)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS coingecko (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                project TEXT,
                twitter_followers INTEGER,
                telegram_channel_user_count INTEGER,
                UNIQUE(date, project)
            )
        ''')

        conn.commit()
    except Exception as e:
        traceback.print_exc() 
        print(f"An unexpected error occurred: {e}")
    finally:
        cursor.close()
        conn.close()
