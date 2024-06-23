from googleapiclient.discovery import build
import os
import traceback
import sqlite3
import time

from ..utils import get_start_end_of_day, parse_date_string
from .set import set_youtube_in_charts, add_to_youtube_ignore_list, delete_youtube_ignore_list, delete_youtube_ignore_row
from .get import get_youtube_ignore_list
from ..const import DATABASE
from projects.youtube_popular import YOUTUBE_POPULAR


def start_youtube():
    youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))
    return youtube

def get_number_of_videos(keyword, youtube, all_popular, published_after=None, published_before=None):
    max_results = 50 
    number_of_videos = 0
    next_page_token = None
    popular_names = set()
    
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
        for item in items:
            channel_title = item['snippet']['channelTitle']
            if item['snippet']['channelTitle'] in all_popular:
                popular_names.add(channel_title)
        number_of_videos += len(items)
        next_page_token = search_response.get('nextPageToken')
        
        if not next_page_token:
            break
    return number_of_videos, total_results, popular_names
    
def search_youtube(date_project, projects):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    youtube = start_youtube()
    all_popular = YOUTUBE_POPULAR
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
            keywords = project.get('youtube_keywords', [])
            if not keywords:
                print(f'{project_name} no keywords.')
                continue
            if input_project and input_project != project_name:
                continue
            if not input_project and project_name in ignore_list:
                print(f'{project_name} in ignore list.')
                continue
            keywords = project.get('youtube_keywords', [])
            number_of_videos = 0
            number_of_videos_approx = 0
            popular_names = set()
            for keyword in keywords:
                number_of_videos, number_of_videos_approx, popular_names = get_number_of_videos(
                  keyword, youtube, all_popular, published_after, published_before
                )
                set_youtube_in_charts(date, project_name, keyword, number_of_videos, number_of_videos_approx, popular_names, cursor)
            add_to_youtube_ignore_list(date, project_name, cursor)
            conn.commit()
            print(f'{project_name},')
            if input_project:
                return
        delete_youtube_ignore_row(date, conn, cursor)
    except Exception as e:
        traceback.print_exc() 
        print(f"An unexpected error occurred: {e}")
    finally:
        cursor.close()
        conn.close()