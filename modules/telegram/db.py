import json
import sqlite3
import traceback
from datetime import datetime

from ..chatbot.chatbot import complete_complex_chat
from ..const import (DATABASE, KEY_WORDS, MAX_MESSAGES_FOR_CHATBOT,
                     NEW_CHANNEL_LAST_MESSAGES_AMOUNT, SPLIT_LENGTH_FOR_PROMPT, MAX_PARTS_FOR_CHATBOT)
from ..utils import split_prompt

chatbot_description = 'This is chat of a crypto project.'

chatbot_questions = [
  'Are there releases, launches or listings planned? If yes what is the date?',
  'What events are happening or planned to happen soon? If yes what is the date?',
  'Are there any new features planned?',
]
    
def write_new_messages_to_db(all_new_messages):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        for new_messages_of_channel in all_new_messages:
            channel = new_messages_of_channel['channel']
            project = new_messages_of_channel['project']
            messages_by_date = {}  
            for message in new_messages_of_channel['messages']:
                date = message['date'][:10]
                if date not in messages_by_date:
                    messages_by_date[date] = []
                messages_by_date[date].append(message) 
            for date, messages in messages_by_date.items():
                cursor.execute('''
                    SELECT messages, project FROM telegram_messages
                    WHERE date=? AND channel=?
                ''', (date, channel))  
                result = cursor.fetchone()
                if result:
                    existing_messages = json.loads(result[0])
                    existing_project = result[1]
                    existing_messages.extend(messages)
                    updated_messages = json.dumps(existing_messages)     
                    if existing_project != project:
                        cursor.execute('''
                            UPDATE telegram_messages
                            SET project=?, messages=?, messages_count=?
                            WHERE date=? AND channel=?
                        ''', (project, updated_messages, len(existing_messages), date, channel))
                    else:
                        cursor.execute('''
                            UPDATE telegram_messages
                            SET messages=?, messages_count=?
                            WHERE date=? AND channel=?
                        ''', (updated_messages, len(existing_messages), date, channel))
                else:
                    cursor.execute('''
                        INSERT INTO telegram_messages (date, channel, project, messages, messages_count)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (date, channel, project, json.dumps(messages), len(messages)))
                conn.commit()
    except Exception as e:
        traceback.print_exc() 
        print(f"An unexpected error occurred: {e}")
    finally:
        cursor.close()
        conn.close()

def get_last_message_ids():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT channel, last_id FROM telegram_last_ids')
        rows = cursor.fetchall()
    except Exception as e:
        traceback.print_exc() 
        print(f"An unexpected error occurred: {e}")
    finally:
        cursor.close()
        conn.close()
    return {row[0]: row[1] for row in rows}

def update_last_message_ids(last_message_ids):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        for channel, last_id in last_message_ids.items():
            cursor.execute('''
                INSERT INTO telegram_last_ids (channel, last_id)
                VALUES (?, ?)
                ON CONFLICT(channel) DO UPDATE SET last_id=excluded.last_id
            ''', (channel, last_id))
        conn.commit()
    except Exception as e:
        traceback.print_exc() 
        print(f"An unexpected error occurred: {e}")
    finally:
        cursor.close()
        conn.close()
        
def get_messages_by_date_and_channel(date, channel=''):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    result = []
    try:
        if channel:
            cursor.execute('''
                SELECT channel, project, messages 
                FROM telegram_messages
                WHERE date=? AND channel=?
            ''', (date, channel))
        else:
            cursor.execute('''
                SELECT channel, project, messages 
                FROM telegram_messages
                WHERE date=?
            ''', (date,))
        rows = cursor.fetchall()
        for row in rows:
            channel, project, messages_json = row
            messages = json.loads(messages_json)
            result.append({
                "channel": channel,
                "project": project,
                "messages": messages
            })
    except Exception as e:
        traceback.print_exc() 
        print(f"An unexpected error occurred: {e}")
    finally:
        cursor.close()
        conn.close()
        return result
    
def update_chatbot_answers(messages_by_date, date):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        for messages_of_channel in messages_by_date:
            channel = messages_of_channel['channel']
            try:
                splitted_data = split_prompt(json.dumps(messages_of_channel), SPLIT_LENGTH_FOR_PROMPT, chatbot_description, chatbot_questions)
                splitted_length = len(splitted_data)
                if splitted_length > MAX_PARTS_FOR_CHATBOT:
                    print(f'{date} {channel} ignored. Too many data. {splitted_length} parts.')
                    continue
                answers = complete_complex_chat(splitted_data)
                answers_str = '\n\n'.join(answers)
                cursor.execute("UPDATE telegram_messages SET chatbot_answer=? WHERE date=? AND channel=?", (answers_str, date, channel))
                conn.commit()
                print(f'{date} {channel} completed')
            except Exception as e:
                traceback.print_exc() 
                print(f"An unexpected error occurred: {e}")
                print(f'{date} {channel} is not completed')
    finally:
        cursor.close()
        conn.close()
    
def clean_chatbot_answers():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE telegram_messages SET chatbot_answer = '', chatbot_filter = ''")
        conn.commit()
    except Exception as e:
        traceback.print_exc() 
        print(f"An unexpected error occurred: {e}")
    finally:
        cursor.close()
        conn.close()
    
def get_chatbot_answers_by_date(date):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    result = []
    try:
        cursor.execute('''
            SELECT channel, chatbot_answer 
            FROM telegram_messages
            WHERE date=?
        ''', (date,))
        rows = cursor.fetchall()        
        for row in rows:
            channel, chatbot_answer = row
            if chatbot_answer:
                result.append({
                    'channel': channel,
                    'chatbot_answer': chatbot_answer
                })          
    except Exception as e:
        traceback.print_exc() 
        print(f"An unexpected error occurred: {e}")
    finally:
        cursor.close()
        conn.close()
        return result
  
def update_answer_search(date, answers, keywords):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        for answer in answers:
            channel = answer['channel']
            chatbot_answer = answer['chatbot_answer']
            chatbot_answer_lower = chatbot_answer.lower()
            updates = []
            for keyword in keywords['upper']:
                if keyword in chatbot_answer:
                    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    update_text = f"{current_time} Found {keyword}"
                    updates.append(update_text)
            for keyword in keywords['lower']:
                if keyword in chatbot_answer_lower:
                    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    update_text = f"{current_time} Found {keyword}"
                    updates.append(update_text)
            if updates:
                cursor.execute("SELECT chatbot_filter FROM telegram_messages WHERE date=? AND channel=?", (date, channel))
                row = cursor.fetchone()
                existing_filter = row[0] if row and row[0] else ""
                updated_filter = existing_filter + "\n" + "\n".join(updates) if existing_filter else "\n".join(updates)
                cursor.execute("UPDATE telegram_messages SET chatbot_filter=? WHERE date=? AND channel=?", (updated_filter, date, channel))
            conn.commit()
    except Exception as e:
        traceback.print_exc() 
        print(f"An unexpected error occurred: {e}")
    finally:
        cursor.close()
        conn.close()
        
def clean_answer_search():
  conn = sqlite3.connect(DATABASE)
  cursor = conn.cursor()
  try:
      cursor.execute("UPDATE telegram_messages SET chatbot_filter = ''")
      conn.commit()
  except Exception as e:
      traceback.print_exc() 
      print(f"An unexpected error occurred: {e}")
  finally:
      cursor.close()
      conn.close()
    