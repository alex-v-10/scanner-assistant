import sqlite3
import traceback

from ..telegram.get import get_messages_sum
from ..const import DATABASE
from ..utils import get_past_dates

def set_telegram_in_charts(date, project, cursor):
    messages_sum = get_messages_sum(date, project, cursor)  
    cursor.execute('''
        INSERT INTO charts (date, project, telegram)
        VALUES (?, ?, ?)
        ON CONFLICT(date, project) DO UPDATE SET telegram = excluded.telegram
    ''', (date, project, messages_sum))

def update_charts(number, projects):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    dates = get_past_dates(number)
    try:
        for date in dates:
            for project in projects:
                set_telegram_in_charts(date, project['project'], cursor)
        conn.commit()
    except Exception as e:
        traceback.print_exc() 
        print(f"An unexpected error occurred: {e}")
    finally:
        cursor.close()
        conn.close()
    
    