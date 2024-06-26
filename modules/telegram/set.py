import json

from datetime import datetime, timezone

def set_telegram_min_id(channel, min_id, cursor):
    cursor.execute('''
        INSERT INTO telegram_min_ids (channel, min_id)
        VALUES (?, ?)
        ON CONFLICT(channel) DO UPDATE SET min_id=excluded.min_id
    ''', (channel, min_id))
    
def set_new_telegram_messages(channel, project, new_messages, cursor):
    messages_by_date = {}  
    for message in new_messages:
        date = message['date'][:10]
        if date not in messages_by_date:
            messages_by_date[date] = []
        messages_by_date[date].append(message) 
    for date, messages in messages_by_date.items():
        cursor.execute('''
            SELECT messages, project FROM telegram
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
                    UPDATE telegram
                    SET project=?, messages=?, messages_count=?
                    WHERE date=? AND channel=?
                ''', (project, updated_messages, len(existing_messages), date, channel))
            else:
                cursor.execute('''
                    UPDATE telegram
                    SET messages=?, messages_count=?
                    WHERE date=? AND channel=?
                ''', (updated_messages, len(existing_messages), date, channel))
        else:
            cursor.execute('''
                INSERT INTO telegram (date, channel, project, messages, messages_count)
                VALUES (?, ?, ?, ?, ?)
            ''', (date, channel, project, json.dumps(messages), len(messages)))
            
def set_chatbot_answer(date, channel, answer, cursor):
    cursor.execute('''
        UPDATE telegram
        SET chatbot_answer=? 
        WHERE date=? AND channel=?
    ''', (answer, date, channel))
    
# def set_answer_search(date, channel, search_results, cursor):
#     cursor.execute("SELECT answer_search FROM telegram WHERE date=? AND channel=?", (date, channel))
#     row = cursor.fetchone()
#     existing_data = row[0] if row and row[0] else ""
#     current_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S') + "\n"
#     if existing_data:
#         updated_data = existing_data + "\n\n\n" + current_time + "\n\n".join(search_results)
#     else:
#         updated_data = current_time + "\n\n".join(search_results)
#     cursor.execute("UPDATE telegram SET answer_search=? WHERE date=? AND channel=?", (updated_data, date, channel))

def set_search_column(date, channel, found_messages, cursor, column):
    if found_messages:
        messages_to_write = json.dumps(found_messages)
    else:
        messages_to_write = None
    cursor.execute(f'''
        UPDATE telegram
        SET {column} = ?
        WHERE date = ? AND channel = ?
    ''', (messages_to_write, date, channel))
    
def add_channel_to_ignore_list(date, channel, cursor):
    cursor.execute('SELECT telegram_channels FROM ignore_list WHERE date = ?', (date,))
    row = cursor.fetchone()
    if row:
        existing_channels = row[0]
        if not existing_channels:
            existing_channels = ''
        updated_channels = existing_channels + ',' + channel
        cursor.execute('UPDATE ignore_list SET telegram_channels = ? WHERE date = ?', (updated_channels, date))
    else:
        cursor.execute('INSERT INTO ignore_list (date, telegram_channels) VALUES (?, ?)', (date, channel))

def delete_telegram_ignore_list(date, conn, cursor):
    cursor.execute('''
        UPDATE ignore_list
        SET telegram_channels = NULL
        WHERE date = ?
    ''', (date,))
    conn.commit()
    
def delete_telegram_ignore_row(date, conn, cursor):
    cursor.execute('''
        UPDATE ignore_list
        SET telegram_channels = NULL
        WHERE date = ?
    ''', (date,))
    cursor.execute('''
        SELECT youtube, coingecko
        FROM ignore_list
        WHERE date = ?
    ''', (date,))
    row = cursor.fetchone()
    if row and row[0] is None and row[1] is None:
        cursor.execute('''
            DELETE FROM ignore_list
            WHERE date = ?
        ''', (date,))
    conn.commit()