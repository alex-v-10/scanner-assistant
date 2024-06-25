def set_community_data(
        date,
        project,
        twitter_followers,
        telegram_channel_user_count,
        cursor
    ):
    cursor.execute('''
        SELECT id FROM coingecko
        WHERE date = ? AND project = ?
    ''', (date, project))
    if cursor.fetchone() is None:
        cursor.execute('''
            INSERT INTO coingecko (
                date,
                project,
                twitter_followers,
                telegram_channel_user_count
            )
            VALUES (?, ?, ?, ?)
        ''', (
            date,
            project,
            twitter_followers,
            telegram_channel_user_count
        ))
    else:
        cursor.execute('''
            UPDATE coingecko
            SET twitter_followers = ?,
                telegram_channel_user_count = ?
            WHERE date = ? AND project = ?
        ''', (
            twitter_followers,
            telegram_channel_user_count,
            date,
            project
        ))

def add_coingecko_to_ignore_list(date, project, cursor):
    cursor.execute('SELECT coingecko FROM ignore_list WHERE date = ?', (date,))
    row = cursor.fetchone()
    if row:
        existing_projects = row[0]
        if not existing_projects:
            existing_projects = ''
        updated_projects = existing_projects + ',' + project
        cursor.execute('UPDATE ignore_list SET coingecko = ? WHERE date = ?', (updated_projects, date))
    else:
        cursor.execute('INSERT INTO ignore_list (date, coingecko) VALUES (?, ?)', (date, project))

def delete_coingecko_ignore_list(date, conn, cursor):
    cursor.execute('''
        UPDATE ignore_list
        SET coingecko = NULL
        WHERE date = ?
    ''', (date,))
    conn.commit()
    
def delete_coingecko_ignore_row(date, conn, cursor):
    cursor.execute('''
        UPDATE ignore_list
        SET coingecko = NULL
        WHERE date = ?
    ''', (date,))
    cursor.execute('''
        SELECT youtube, telegram_channels
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