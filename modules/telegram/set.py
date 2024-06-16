import json

def set_last_message_id(channel, last_message_id, cursor):
    cursor.execute('''
        INSERT INTO telegram_last_ids (channel, last_id)
        VALUES (?, ?)
        ON CONFLICT(channel) DO UPDATE SET last_id=excluded.last_id
    ''', (channel, last_message_id))
    
def set_new_telegram_messages(channel, project, new_messages, cursor):
    messages_by_date = {}  
    for message in new_messages:
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
            
def set_chatbot_answer(date, channel, answer, conn, cursor):
    cursor.execute('''
        UPDATE telegram_messages
        SET chatbot_answer=? 
        WHERE date=? AND channel=?
    ''', (answer, date, channel))
    conn.commit()
    print(f'"{channel}",')
    
def set_answer_search(date, channel, search_results, cursor):
    cursor.execute("SELECT answer_search FROM telegram_messages WHERE date=? AND channel=?", (date, channel))
    row = cursor.fetchone()
    existing_data = row[0] if row and row[0] else ""
    updated_data = existing_data + "\n\n" + "\n\n".join(search_results) if existing_data else "\n\n".join(search_results)
    cursor.execute("UPDATE telegram_messages SET answer_search=? WHERE date=? AND channel=?", (updated_data, date, channel))
    
def set_messages_search(date, channel, found_messages, cursor):
    messages_to_write = json.dumps(found_messages)
    cursor.execute('''
        UPDATE telegram_messages
        SET messages_search = ?
        WHERE date = ? AND channel = ?
    ''', (messages_to_write, date, channel)) 