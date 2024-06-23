def set_youtube_in_charts(date, project, number, number_approx, popular_found, cursor):
    popular = len(popular_found)
    popular_list = ','.join(popular_found)
    cursor.execute('''
        SELECT id FROM youtube
        WHERE date = ? AND project = ?
    ''', (date, project))
    if cursor.fetchone() is None:
        cursor.execute('''
            INSERT INTO youtube (date, project, videos, videos_approx, popular, popular_list)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (date, project, number, number_approx, popular, popular_list))
    else:
        cursor.execute('''
            UPDATE youtube
            SET videos = ?, videos_approx = ?, popular = ?, popular_list = ?
            WHERE date = ? AND project = ?
        ''', (number, number_approx, popular, popular_list, date, project))

def add_to_youtube_ignore_list(date, project, cursor):
    cursor.execute('SELECT youtube FROM ignore_list WHERE date = ?', (date,))
    row = cursor.fetchone()
    if row:
        existing_projects = row[0]
        if not existing_projects:
            existing_projects = ''
        updated_projects = existing_projects + ',' + project
        cursor.execute('UPDATE ignore_list SET youtube = ? WHERE date = ?', (updated_projects, date))
    else:
        cursor.execute('INSERT INTO ignore_list (date, youtube) VALUES (?, ?)', (date, project))
        
def delete_youtube_ignore_list(date, conn, cursor):
    cursor.execute('''
        UPDATE ignore_list
        SET youtube = NULL
        WHERE date = ?
    ''', (date,))
    conn.commit()
    
def delete_youtube_ignore_row(date, conn, cursor):
    cursor.execute('''
        UPDATE ignore_list
        SET youtube = NULL
        WHERE date = ?
    ''', (date,))
    cursor.execute('''
        SELECT telegram_channels
        FROM ignore_list
        WHERE date = ?
    ''', (date,))
    row = cursor.fetchone()
    if row and row[0] is None:
        cursor.execute('''
            DELETE FROM ignore_list
            WHERE date = ?
        ''', (date,))
    conn.commit()