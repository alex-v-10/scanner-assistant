from googleapiclient.discovery import build
import json
import os
import traceback
import sqlite3
import time

from ..utils import get_start_end_of_day, get_today_start, parse_date_string, get_current_date
from .set import set_youtube_in_charts, add_to_youtube_ignore_list, delete_youtube_ignore_list
from .get import get_youtube_ignore_list
from ..const import DATABASE


def start_youtube():
    youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))
    return youtube
#TODO
def get_approx_number_of_videos(keyword, youtube, published_after=None, published_before=None):
    try:
        search_request = youtube.search().list(
            q=keyword,
            type='video',
            part='id,snippet',  # Include snippet part to get video details
            maxResults=50,      # Adjust maxResults as needed
            publishedAfter=published_after,
            publishedBefore=published_before
        )
        search_response = search_request.execute()
        total_results = search_response['pageInfo']['totalResults']
        video_names = [item['snippet']['title'] for item in search_response.get('items', [])]

        return total_results, video_names
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, []

def get_number_of_videos(keyword, youtube, published_after=None, published_before=None):
    max_results = 50 
    number_of_videos = 0
    next_page_token = None
    
    for _ in range(1):
        print('query')
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
        items = search_response.get('items', [])
        number_of_videos += len(items)
        next_page_token = search_response.get('nextPageToken')
        
        if not next_page_token:
            break
    return number_of_videos
      
def test_youtube():    
    youtube = start_youtube()
    text_date = input('Input what to search (keyword:YYYY-MM-DD): ')
    text_date_parts = text_date.split(':', 1)
    text = text_date_parts[0]
    if len(text_date_parts) > 1:
        date = text_date_parts[1]
    else:
        date = None
    published_after, published_before = get_start_end_of_day(date)  
    result = get_number_of_videos(text, youtube, published_after, published_before)
    print(result[0])
    # print(len(result[1]))
    
def search_youtube(date, projects):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        youtube = start_youtube()
        published_after, published_before = get_start_end_of_day(date)
        date = parse_date_string(published_after)
        ignore_list = get_youtube_ignore_list(date, cursor)
        for project in projects:
            time.sleep(3)
            project_name = project['project']
            if project_name in ignore_list:
                print(f'{project_name} in ignore list.')
                continue
            keywords = project.get('youtube_keywords', [])
            number_of_videos_list = [0]
            for keyword in keywords:
                number_of_videos = get_number_of_videos(keyword, youtube, published_after, published_before)
                number_of_videos_list.append(number_of_videos)
            result_number = max(number_of_videos_list)
            set_youtube_in_charts(date, project_name, result_number, cursor)
            add_to_youtube_ignore_list(date, project_name, cursor)
            conn.commit()
            print(f'{project_name},')
        delete_youtube_ignore_list(date, conn, cursor)
    except Exception as e:
        traceback.print_exc() 
        print(f"An unexpected error occurred: {e}")
    finally:
        cursor.close()
        conn.close()