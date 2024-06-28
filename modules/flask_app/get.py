import sqlite3
import json
import traceback

from ..const import DATABASE

def get_search_db(date):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    data = {}
    try:
        cursor.execute('SELECT project, messages FROM search WHERE date = ?', (date,))
        rows = cursor.fetchall()
        for row in rows:
            project, messages_str = row
            messages = json.loads(messages_str)
            if project in data:
                data[project].extend(messages)
            else:
                data[project] = messages    
    except Exception as e:
        traceback.print_exc() 
        print(f"An unexpected error occurred: {e}")
        return None
    finally:
        cursor.close()
        conn.close()
    return data
  
def get_projects_db():
  conn = sqlite3.connect(DATABASE)
  cursor = conn.cursor()
  data = {}
  try:
      cursor.execute('SELECT * FROM projects')
      rows = cursor.fetchall()
      for row in rows:
          project, is_favorite, is_hidden = row
          data[project] = {
            'is_favorite': bool(is_favorite),
            'is_hidden': bool(is_hidden),
          }     
  except Exception as e:
      traceback.print_exc() 
      print(f"An unexpected error occurred: {e}")
      return None
  finally:
      cursor.close()
      conn.close()
  return data