import json
import os
import config

from dotenv import load_dotenv
from telethon.sync import TelegramClient
from .utils import split_prompt, delete_folder, delete_file

load_dotenv()
api_id = os.getenv('TELEGRAM_API_ID')
api_hash = os.getenv('TELEGRAM_API_HASH')
phone_number = os.getenv('TELEGRAM_PHONE_NUMBER')
channel_names = os.getenv('TELEGRAM_CHANNEL_NAMES').split(',')

client = TelegramClient('session_name', api_id, api_hash)

async def get_unread_counts(last_message_ids):
    unread_counts = {}
    for channel_name in channel_names:
        channel = await client.get_entity(channel_name)
        async for message in client.iter_messages(channel, limit=1):
            message_id = message.id
            if channel_name in last_message_ids:
                last_message_id = last_message_ids[channel_name]
                difference = message_id - last_message_id
            else:
                last_message_id = message_id
                difference = config.NEW_CHANNEL_LAST_MESSAGES_AMOUNT
            unread_counts[channel_name] = difference
            last_message_ids[channel_name] = message_id
    return unread_counts
  
async def get_all_new_messages(last_message_ids):
    unread_counts = await get_unread_counts(last_message_ids)
    all_new_messages = []
    for channel_name in channel_names:
          if channel_name in unread_counts and unread_counts[channel_name] > 0:
              channel = await client.get_entity(channel_name)
              new_messages_of_channel = {
                  'channel': channel_name,
                  'messages': []
              }
              async for message in client.iter_messages(channel, limit=unread_counts[channel_name]):
                  new_messages_of_channel['messages'].append({
                      'message_date': message.date.isoformat(),
                      'content': message.text,
                  })
              all_new_messages.append(new_messages_of_channel)
    return all_new_messages
  
def save_messages_to_json(all_new_messages):
    updated_channels=[]
    for new_messages_of_channel in all_new_messages:
        channel_name = new_messages_of_channel['channel']

        if not os.path.exists(f'data/json_messages'):
            os.makedirs(f'data/json_messages')
        
        with open(f'data/json_messages/{channel_name}.json', 'w', encoding='utf-8') as f:
            json.dump(new_messages_of_channel, f, ensure_ascii=False, indent=4)
        updated_channels.append(channel_name)
        
    for channel_name in channel_names:
        if channel_name not in updated_channels:
            delete_file(f'data/json_messages/{channel_name}.json')
    
    
        
def save_messages_to_splitted_txt(all_new_messages):
    updated_channels=[]
    for new_messages_of_channel in all_new_messages:
        channel_name = new_messages_of_channel['channel']

        if not os.path.exists(f'data/splitted_messages'):
            os.makedirs(f'data/splitted_messages')

        if not os.path.exists(f'data/splitted_messages/{channel_name}'):
            os.makedirs(f'data/splitted_messages/{channel_name}')
        
        new_messages_of_channel_mod = {
            'channel': channel_name,
            'messages': []
        }
        
        for message in new_messages_of_channel['messages']:
            new_messages_of_channel_mod['messages'].append({
                'message_start': '(',
                'message_date': message['message_date'],
                'content': message['content'],
                'message_end': ')'
            })
        
        splitted_data = split_prompt(json.dumps(new_messages_of_channel_mod), config.SPLIT_LENGTH_FOR_PROMPT)
        
        for data_item in splitted_data:
            with open(f'data/splitted_messages/{channel_name}/{data_item['name']}.txt', 'w', encoding='utf-8') as f:
                f.write(data_item['content'])
        updated_channels.append(channel_name)
        
    for channel_name in channel_names:
        if channel_name not in updated_channels:
            delete_folder(f'data/splitted_messages/{channel_name}')

async def save_telegram_messages():
    await client.start(phone_number)
    
    if os.path.exists('data/last_message_ids.json'):
        with open('data/last_message_ids.json', 'r', encoding='utf-8') as f:
            last_message_ids = json.load(f)
    else:
        last_message_ids = {}
    
    all_new_messages = await get_all_new_messages(last_message_ids)
    
    save_messages_to_json(all_new_messages)
    save_messages_to_splitted_txt(all_new_messages)
        
    with open('data/last_message_ids.json', 'w', encoding='utf-8') as f:
        json.dump(last_message_ids, f, ensure_ascii=False, indent=4)