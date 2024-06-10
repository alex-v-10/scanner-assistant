import sqlite3
import json

def insert_messages(channel, project, date, messages):
    conn = sqlite3.connect('info.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO telegram_messages (channel, project, date, messages)
        VALUES (?, ?, ?, ?)
    ''', (channel, project, date, json.dumps(messages)))
    
    conn.commit()
    conn.close()
    
def write_new_messages_to_db(all_new_messages):
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
            conn = sqlite3.connect('info.db')
            cursor = conn.cursor()
            cursor.execute('''
                SELECT messages FROM telegram_messages
                WHERE channel=? AND date=?
            ''', (channel, date))
            existing_messages = cursor.fetchone()

            if existing_messages:
                existing_messages = json.loads(existing_messages[0])
                existing_messages.extend(messages)
                updated_messages = json.dumps(existing_messages)
                cursor.execute('''
                    UPDATE telegram_messages
                    SET messages=?
                    WHERE channel=? AND date=?
                ''', (updated_messages, channel, date))
            else:
                insert_messages(channel, project, date, messages)
            
            conn.commit()
            conn.close()

def get_last_message_ids():
    conn = sqlite3.connect('info.db')
    cursor = conn.cursor()
    cursor.execute('SELECT channel, last_id FROM telegram_last_ids')
    rows = cursor.fetchall()
    conn.close()
    return {row[0]: row[1] for row in rows}

def update_last_message_ids(last_message_ids):
    for channel, last_id in last_message_ids.items():
        conn = sqlite3.connect('info.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO telegram_last_ids (channel, last_id)
            VALUES (?, ?)
            ON CONFLICT(channel) DO UPDATE SET last_id=excluded.last_id
        ''', (channel, last_id))
        conn.commit()
        conn.close()
    