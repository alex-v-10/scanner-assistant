from googleapiclient.discovery import build
import os
import traceback
import sqlite3

from ..utils import get_start_end_of_day, parse_date_string
from .set import set_youtube_in_charts, add_to_youtube_ignore_list, delete_youtube_ignore_list, set_youtube_approx_in_charts
from .get import get_youtube_ignore_list
from ..const import DATABASE


def start_youtube():
    youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))
    return youtube

def get_number_of_videos(keyword, youtube, published_after=None, published_before=None):
    max_results = 50 
    number_of_videos = 0
    next_page_token = None
    
    for _ in range(1):
        print('- youtube query')
        search_request = youtube.search().list(
            q=keyword,
            type='video',
            part='id,snippet',
            maxResults=max_results,
            pageToken=next_page_token,
            publishedAfter=published_after,
            publishedBefore=published_before
        )
        search_response = search_request.execute()
        total_results = search_response['pageInfo']['totalResults']
        items = search_response.get('items', [])
        number_of_videos += len(items)
        next_page_token = search_response.get('nextPageToken')
        
        if not next_page_token:
            break
    return number_of_videos, total_results
    
def search_youtube(date_project, projects):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    youtube = start_youtube()
    date_project_parts = date_project.split(' ', 1)
    date = date_project_parts[0]
    input_project = None
    if len(date_project_parts) > 1:
        input_project = date_project_parts[1]
    try:
        published_after, published_before = get_start_end_of_day(date)
        date = parse_date_string(published_after)
        print(date)
        if not input_project:
            ignore_list = get_youtube_ignore_list(date, cursor)
            if ignore_list:
                choice = input('Do you want to continue (y) or start from beginning (n)? y/n: ')
                if choice == 'n':
                    ignore_list = []
                    delete_youtube_ignore_list(date, conn, cursor)
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
            keywords = project.get('youtube_keywords', [])
            number_of_videos_list = [0]
            number_of_videos_approx_list = [0]
            for keyword in keywords:
                number_of_videos, number_of_videos_approx = get_number_of_videos(keyword, youtube, published_after, published_before)
                number_of_videos_list.append(number_of_videos)
                number_of_videos_approx_list.append(number_of_videos_approx)
            result_number = max(number_of_videos_list)
            result_number_approx = max(number_of_videos_approx_list)
            set_youtube_in_charts(date, project_name, result_number, cursor)
            set_youtube_approx_in_charts(date, project_name, result_number_approx, cursor)
            add_to_youtube_ignore_list(date, project_name, cursor)
            conn.commit()
            print(f'{project_name},')
            if input_project:
                return
        delete_youtube_ignore_list(date, conn, cursor)
    except Exception as e:
        traceback.print_exc() 
        print(f"An unexpected error occurred: {e}")
    finally:
        cursor.close()
        conn.close()