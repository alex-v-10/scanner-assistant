import json
import os

from dotenv import load_dotenv
from telethon.sync import TelegramClient
from ..utils import split_prompt, delete_folder, delete_file
from ..const import NEW_CHANNEL_LAST_MESSAGES_AMOUNT, SPLIT_LENGTH_FOR_PROMPT, KEY_WORDS
from .db import write_new_messages_to_db, get_last_message_ids, update_last_message_ids

load_dotenv()
api_id = os.getenv('TELEGRAM_API_ID')
api_hash = os.getenv('TELEGRAM_API_HASH')
phone_number = os.getenv('TELEGRAM_PHONE_NUMBER')
# channel_names = os.getenv('TELEGRAM_CHANNEL_NAMES').split(',')

with open('projects.json', 'r') as f:
    projects = json.load(f)
project_names = [project['project'] for project in projects]

client = TelegramClient('session_name', api_id, api_hash)

async def get_all_new_messages(last_message_ids):
    all_new_messages = []
    for project in projects:
        for channel_name in project['telegram_channels']:
            channel = await client.get_entity(channel_name)
            new_messages_of_channel = {
                'channel': channel_name,
                'project': project['project'],
                'messages': []
            }
            isFirst = True
            min_id = int(last_message_ids.get(channel_name, 0))
            limit = None if min_id else NEW_CHANNEL_LAST_MESSAGES_AMOUNT
            async for message in client.iter_messages(channel, min_id=min_id, limit=limit):
                if isFirst:
                    last_message_ids[channel_name] = message.id
                    isFirst = False
                new_messages_of_channel['messages'].insert(0, {
                    'id': message.id,
                    'date': message.date.isoformat(),
                    'content': message.text,
                })
            if new_messages_of_channel['messages']:
                all_new_messages.append(new_messages_of_channel)
    return all_new_messages
  
# def get_all_splitted_messages(all_new_messages):
#     all_splitted_messages = []
#     for new_messages_of_channel in all_new_messages:
#         channel_name = new_messages_of_channel['channel']
#         splitted_data = split_prompt(json.dumps(new_messages_of_channel), SPLIT_LENGTH_FOR_PROMPT)
#         all_splitted_messages.append({
#             'channel': channel_name,
#             'messages': splitted_data
#         })
#     return all_splitted_messages
  
# def get_new_important_messages(all_new_messages):
#     new_important_messages = []
#     for new_messages_of_channel in all_new_messages:
#         channel_name = new_messages_of_channel['channel']
#         new_important_messages_of_channel = {
#             'channel': channel_name,
#             'messages': []
#         }
#         for message in new_messages_of_channel['messages']:
#             if message['content'] is None:
#                 continue
#             for word in KEY_WORDS['priority1']:
#                 if word in message['content'].lower():
#                     new_important_messages_of_channel['messages'].append(message)
#                     break
#         if new_important_messages_of_channel['messages']:
#             new_important_messages.append(new_important_messages_of_channel)
#     return new_important_messages
  
def save_messages_to_json(all_new_messages):
    updated_channels=[]
    for new_messages_of_channel in all_new_messages:
        channel_name = new_messages_of_channel['channel']
        project_name = new_messages_of_channel['project']

        if not os.path.exists(f'data/json_messages'):
            os.makedirs(f'data/json_messages')
        
        with open(f'data/json_messages/{channel_name}({project_name}).json', 'w', encoding='utf-8') as f:
            json.dump(new_messages_of_channel, f, ensure_ascii=False, indent=4)
        updated_channels.append(channel_name)
        
    for project in projects:
        for channel_name in project['telegram_channels']:
            if channel_name not in updated_channels:
                delete_file(f'data/json_messages/{channel_name}({project['project']}).json')
            
      
# def save_splitted_messages(all_splitted_messages):
#     updated_channels=[]
#     for splitted_messages_of_channel in all_splitted_messages:
#         channel_name = splitted_messages_of_channel['channel']

#         if not os.path.exists(f'data/splitted_messages'):
#             os.makedirs(f'data/splitted_messages')

#         if not os.path.exists(f'data/splitted_messages/{channel_name}'):
#             os.makedirs(f'data/splitted_messages/{channel_name}')
        
#         for messages_item in splitted_messages_of_channel['messages']:
#             with open(f'data/splitted_messages/{channel_name}/{messages_item['name']}.txt', 'w', encoding='utf-8') as f:
#                 f.write(messages_item['content'])
#         updated_channels.append(channel_name)
        
#     for channel_name in channel_names:
#         if channel_name not in updated_channels:
#             delete_folder(f'data/splitted_messages/{channel_name}')

async def save_telegram_messages():
    await client.start(phone_number)
    
    if not os.path.exists(f'data'):
        os.makedirs(f'data')
        
    #TODO Use db and add project_names
    
    last_message_ids = get_last_message_ids()
    all_new_messages = await get_all_new_messages(last_message_ids)
    
    write_new_messages_to_db(all_new_messages)
    save_messages_to_json(all_new_messages)
    update_last_message_ids(last_message_ids)