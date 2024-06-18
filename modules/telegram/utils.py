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
        cursor.execute("UPDATE ignore_list SET date = '', telegram_channels=''")
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
      
async def search_channel_ids(telegram_client):
    dialogs = await telegram_client.get_dialogs()
    channels = []
    for dialog in dialogs:
        entity = dialog.entity
        if hasattr(entity, 'broadcast') and entity.broadcast:
            print(f'Channel Name: {entity.title}, Channel ID: {entity.id}')
            channels.append(entity)
    return channels