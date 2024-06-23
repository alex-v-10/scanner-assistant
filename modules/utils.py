import os
import shutil
import re

from datetime import datetime, timedelta, timezone

def delete_folder(folder_path):
    if os.path.exists(folder_path):
        try:
            shutil.rmtree(folder_path)
        except PermissionError:
            print(f"Permission denied: cannot delete {folder_path}")
        except Exception as e:
            print(f"Error deleting folder {folder_path}: {e}")
        
def delete_file(file_path):
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except PermissionError:
            print(f"Permission denied: cannot delete {file_path}")
        except Exception as e:
            print(f"Error occurred while deleting {file_path}: {e}")

def find_dict_by_key_value(dicts, key, value):
    return next((d for d in dicts if d.get(key) == value), None)
        
# def split_prompt(text, split_length, questions):
#     if split_length <= 0:
#         raise ValueError("Max length must be greater than 0.")
#     num_parts = -(-len(text) // split_length)
#     file_data = []
#     for i in range(num_parts):
#         start = i * split_length
#         end = min((i + 1) * split_length, len(text))
#         if i == num_parts - 1:
#             content = f'[START PART {i + 1}/{num_parts}]\n' + text[start:end] + f'\n[END PART {i + 1}/{num_parts}]'
#             content += '\nALL PARTS SENT. Now you can continue processing the request.'
#             content += f'\n{questions}'
#         else:
#             content = f'Do not answer yet. This is just another part of the text I want to send you. Just receive and acknowledge as "Part {i + 1}/{num_parts} received" and wait for the next part.\n[START PART {i + 1}/{num_parts}]\n' + text[start:end] + f'\n[END PART {i + 1}/{num_parts}]'
#             content += f'\nRemember not answering yet. Just acknowledge you received this part with the message "Part {i + 1}/{num_parts} received" and wait for the next part.'
#         file_data.append({
#             'name': f'split_{str(i + 1).zfill(3)}_of_{str(num_parts).zfill(3)}.txt',
#             'content': content
#         })
#     return file_data
  
def split_prompt(text, split_length, description, questions):
    if split_length <= 0:
        raise ValueError("Max length must be greater than 0.")
    num_parts = -(-len(text) // split_length)
    file_data = []
    for i in range(num_parts):
        start = i * split_length
        end = min((i + 1) * split_length, len(text))
        content = text[start:end]
        content += f'\n [END OF LOG] \n{description}\n ANSWER QUESTIONS: \n{questions}'
        file_data.append({
            'prompt': content
        })
    return file_data
  
def extract_context(text, keyword, isUpper=False, context_len=50):
    text = text.replace('\n', ' ')
    contexts = []
    if isUpper:
        index = text.find(keyword)
    else:
        index = text.lower().find(keyword.lower())
    count = 1
    while index != -1:
        start = max(index - context_len, 0)
        end = min(index + len(keyword) + context_len, len(text))
        contexts.append(f'{count}) {text[start:end]}')
        if isUpper:
            index = text.find(keyword, index + 1)
        else:
            index = text.lower().find(keyword.lower(), index + 1)
        count += 1
    return contexts
  
# def find_sentences_with_keyword(text, keyword):
#     text = text.replace('\n', '')
#     sentence_endings = re.compile(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s')
#     sentences = sentence_endings.split(text)
#     found_sentences = set()
#     for sentence in sentences:
#         if re.search(r'\b' + re.escape(keyword) + r'\b', sentence, re.IGNORECASE):
#             found_sentences.add(sentence.strip())
#     return list(found_sentences)
  
def search_keyword_in_text(text, keyword):
    contexts = extract_context(text, keyword)
    search_result = f'Found {keyword}:\n{'\n'.join(contexts)}'
    return search_result
  
def get_current_date():
    return datetime.now(timezone.utc).strftime('%Y-%m-%d')
  
def get_past_dates(number):
    current_date = datetime.now(timezone.utc)
    past_week_dates = [(current_date - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(number)]
    return past_week_dates
      
def get_start_end_of_day(date=None):
    if date:
        start_of_day = datetime.strptime(date, "%Y-%m-%d").replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
    else:
        start_of_day = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)
    return start_of_day.isoformat(), end_of_day.isoformat()
  
def parse_date_string(date_string):
    parsed_date = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S%z').date()
    formatted_date = parsed_date.strftime('%Y-%m-%d')
    return formatted_date
