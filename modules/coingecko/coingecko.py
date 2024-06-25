import requests
import sqlite3
import traceback

from ..const import DATABASE
from .get import get_community_data, get_coingecko_ignore_list
from .set import set_community_data, add_coingecko_to_ignore_list, delete_coingecko_ignore_list, delete_coingecko_ignore_row
from ..utils import get_current_date

        
def collect_data_coingecko(input_project, projects):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    date = get_current_date()
    try:
        if not input_project:
            ignore_list = get_coingecko_ignore_list(date, cursor)
            if ignore_list:
                choice = input('Do you want to continue (y) or start from beginning (n)? y/n: ')
                if choice == 'n':
                    ignore_list = []
                    delete_coingecko_ignore_list(date, conn, cursor)
                elif choice != 'y':
                    print('Skip')
                    return
        for project in projects:
            project_name = project['project']
            if input_project and input_project != project_name:
                continue
            if not input_project and project_name in ignore_list:
                print(f'{project_name} in ignore list.')
                continue
            coin_id = project.get('coin', {}).get('id', None)
            if not coin_id:
                print(f'{project_name} no coin id.')
                if input_project:
                    return
                continue
            community_data = get_community_data(coin_id)
            if community_data:
                twitter_followers = community_data.get('twitter_followers', None)
                telegram_channel_user_count = community_data.get('telegram_channel_user_count', None)
                set_community_data(
                    date,
                    project_name,
                    twitter_followers,
                    telegram_channel_user_count,
                    cursor)
            add_coingecko_to_ignore_list(date, project_name, cursor)
            conn.commit()
            print(f'{project_name},')
            if input_project:
                return
        delete_coingecko_ignore_row(date, conn, cursor)
    except Exception as e:
        traceback.print_exc() 
        print(f"An unexpected error occurred: {e}")
    finally:
        cursor.close()
        conn.close()