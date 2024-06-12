import sqlite3
from ..const import DATABASE

def update_chatbot_answer(new_answers, date, channel_name):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("UPDATE telegram_messages SET chatbot_answer=? WHERE date=? AND channel=?", (new_answers, date, channel_name))
    conn.commit()
    conn.close()
    
def clean_chatbot_answers():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("UPDATE telegram_messages SET chatbot_answer = ''")
    conn.commit()
    conn.close()