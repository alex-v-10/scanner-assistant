from .youtube import start_youtube, get_number_of_videos
from ..utils import get_start_end_of_day

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
    print(result[1])
    # print(len(result[1]))