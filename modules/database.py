import sqlite3
import json

def create_table():
    conn = sqlite3.connect('info.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS channel_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel TEXT,
            date TEXT,
            messages TEXT
        )
    ''')
    conn.commit()
    conn.close()
    
def insert_messages(channel, date, messages):
    conn = sqlite3.connect('info.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO channel_messages (channel, date, messages)
        VALUES (?, ?, ?)
    ''', (channel, date, json.dumps(messages)))
    
    conn.commit()
    conn.close()
    
def write_new_messages_to_db(all_new_messages):
    for new_messages_of_channel in all_new_messages:
        data = new_messages_of_channel
        channel = data['channel']
        messages_by_date = {}
        
        for message in data['messages']:
            date = message['date'][:10]
            if date not in messages_by_date:
                messages_by_date[date] = []
            messages_by_date[date].append(message)
            
        for date, messages in messages_by_date.items():
            conn = sqlite3.connect('info.db')
            cursor = conn.cursor()
            cursor.execute('''
                SELECT messages FROM channel_messages
                WHERE channel=? AND date=?
            ''', (channel, date))
            existing_messages = cursor.fetchone()

            if existing_messages:
                existing_messages = json.loads(existing_messages[0])
                existing_messages.extend(messages)
                updated_messages = json.dumps(existing_messages)
                cursor.execute('''
                    UPDATE channel_messages
                    SET messages=?
                    WHERE channel=? AND date=?
                ''', (updated_messages, channel, date))
            else:
                insert_messages(channel, date, messages)
            
            conn.commit()
            conn.close()
            
def write_db_to_dict():
    conn = sqlite3.connect('info.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM channel_messages')
    rows = cursor.fetchall()
    
    data = {}
    
    for row in rows:
        id = row[0]
        channel = row[1]
        date = row[2]
        messages = json.loads(row[3])
        
        if channel not in data:
            data[channel] = {}
        
        if date not in data[channel]:
            data[channel][date] = {
                'messages': []
            }
        
        data[channel][date]['messages'].extend(messages)
    
    return data