def set_youtube_in_charts(date, project, number, cursor):
    cursor.execute('''
        INSERT INTO charts (date, project, youtube)
        VALUES (?, ?, ?)
        ON CONFLICT(date, project) DO UPDATE SET youtube = excluded.youtube
    ''', (date, project, number))
#TODO increment problem    
def set_youtube_approx_in_charts(date, project, number, cursor):
    cursor.execute('''
        INSERT INTO charts (date, project, youtube_approx)
        VALUES (?, ?, ?)
        ON CONFLICT(date, project) DO UPDATE SET youtube_approx = excluded.youtube_approx
    ''', (date, project, number))

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