import sqlite3
import json

def insert_messages(date, channel, project, messages):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO telegram_messages (date, channel, project, messages, messages_count)
        VALUES (?, ?, ?, ?, ?)
    ''', (date, channel, project, json.dumps(messages), len(messages)))
    
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
            conn = sqlite3.connect('data.db')
            cursor = conn.cursor()
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
                insert_messages(date, channel, project, messages)
            
            conn.commit()
            conn.close()

def get_last_message_ids():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT channel, last_id FROM telegram_last_ids')
    rows = cursor.fetchall()
    conn.close()
    return {row[0]: row[1] for row in rows}

def update_last_message_ids(last_message_ids):
    for channel, last_id in last_message_ids.items():
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO telegram_last_ids (channel, last_id)
            VALUES (?, ?)
            ON CONFLICT(channel) DO UPDATE SET last_id=excluded.last_id
        ''', (channel, last_id))
        conn.commit()
        conn.close()
    