def set_youtube_in_charts(date, project, number, number_approx, cursor):
    cursor.execute('''
        SELECT id FROM charts
        WHERE date = ? AND project = ?
    ''', (date, project))
    if cursor.fetchone() is None:
        cursor.execute('''
            INSERT INTO charts (date, project, youtube, youtube_approx)
            VALUES (?, ?, ?, ?)
        ''', (date, project, number, number_approx))
    else:
        cursor.execute('''
            UPDATE charts
            SET youtube = ?, youtube_approx = ?
            WHERE date = ? AND project = ?
        ''', (number, number_approx, date, project))

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