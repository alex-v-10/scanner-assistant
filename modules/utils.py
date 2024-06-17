import os
import shutil
from datetime import datetime

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
  
def extract_context(text, keyword, isUpper=False, context_len=100):
    if isUpper:
        index = text.find(keyword)
    else:
        index = text.lower().find(keyword.lower())
    if index == -1:
        return None
    start = max(index - context_len, 0)
    end = min(index + len(keyword) + context_len, len(text))
    context = text[start:end]
    return context
  
def search_keyword_in_text(text, keyword):
    context = extract_context(text, keyword)
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    search_result = f'{current_time} Found {keyword}: "{context}"'
    return search_result
