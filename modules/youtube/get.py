def get_youtube_ignore_list(date, cursor):
    cursor.execute('SELECT youtube FROM ignore_list WHERE date = ?', (date,))
    row = cursor.fetchone()
    if row and row[0]:
        return row[0].split(',')
    else:
        return []