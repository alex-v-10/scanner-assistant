import json
import os
import sqlite3
import traceback

from ..const import DATABASE

def save_messages_to_json(channel, project, messages_of_channel):
    if not os.path.exists(f'data/json_messages'):
        os.makedirs(f'data/json_messages')
    with open(f'data/json_messages/{channel}({project}).json', 'w', encoding='utf-8') as f:
        json.dump(messages_of_channel, f, ensure_ascii=False, indent=4)
        
def clean_chatbot_answers():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE telegram_messages SET chatbot_answer = ''")
        conn.commit()
    except Exception as e:
        traceback.print_exc() 
        print(f"An unexpected error occurred: {e}")
    finally:
        cursor.close()
        conn.close()
        
def clean_search():
  conn = sqlite3.connect(DATABASE)
  cursor = conn.cursor()
  try:
      cursor.execute("UPDATE telegram_messages SET answer_search = '', messages_search = ''")
      conn.commit()
  except Exception as e:
      traceback.print_exc() 
      print(f"An unexpected error occurred: {e}")
  finally:
      cursor.close()
      conn.close()