import json
import os

from dotenv import load_dotenv
from telethon.sync import TelegramClient
from .utils import split_prompt, delete_folder, delete_file

load_dotenv()
api_id = os.getenv('TELEGRAM_API_ID')
api_hash = os.getenv('TELEGRAM_API_HASH')
phone_number = os.getenv('TELEGRAM_PHONE_NUMBER')
channel_usernames = os.getenv('TELEGRAM_CHANNEL_USERNAMES').split(',')

client = TelegramClient('session_name', api_id, api_hash)

async def get_unread_counts(last_message_ids):
    unread_counts = {}
    for channel_username in channel_usernames:
        channel = await client.get_entity(channel_username)
        async for message in client.iter_messages(channel, limit=1):
            message_id = message.id
            if channel_username in last_message_ids:
                last_message_id = last_message_ids[channel_username]
                difference = message_id - last_message_id
            else:
                last_message_id = message_id
                difference = 15
            unread_counts[channel_username] = difference
            last_message_ids[channel_username] = message_id
    return unread_counts
  
async def get_new_messages(unread_counts):
    new_messages = []
    for channel_username in channel_usernames:
          if channel_username in unread_counts and unread_counts[channel_username] > 0:
              channel = await client.get_entity(channel_username)
              message_data = {
                  'channel': channel_username,
                  'messages': []
              }
              async for message in client.iter_messages(channel, limit=unread_counts[channel_username]):
                  message_data['messages'].append({
                      'message_start': '[',
                      'message_date': message.date.isoformat(),
                      # 'message_id': message.id,
                      'content': message.text,
                      'message_end': ']',
                  })
              new_messages.append(message_data)
    return new_messages

async def save_telegram_messages():
    await client.start(phone_number)
    
    if os.path.exists('data/last_message_ids.json'):
        with open('data/last_message_ids.json', 'r', encoding='utf-8') as f:
            last_message_ids = json.load(f)
    else:
        last_message_ids = {}
    
    unread_counts = await get_unread_counts(last_message_ids)
    new_messages = await get_new_messages(unread_counts)

    updated_channels=[]
    for message_data in new_messages:
        channel_username = message_data['channel']

        if not os.path.exists(f'data/json_messages'):
            os.makedirs(f'data/json_messages')

        if not os.path.exists(f'data/messages'):
            os.makedirs(f'data/messages')

        if not os.path.exists(f'data/messages/{channel_username}'):
            os.makedirs(f'data/messages/{channel_username}')
        
        with open(f'data/json_messages/{channel_username}.json', 'w', encoding='utf-8') as f:
            json.dump(message_data, f, ensure_ascii=False, indent=4)
        updated_channels.append(channel_username)
        
        splitted_data = split_prompt(json.dumps(message_data), 2000)
        for data_item in splitted_data:
            with open(f'data/messages/{channel_username}/{data_item['name']}.txt', 'w', encoding='utf-8') as f:
                f.write(data_item['content'])
        updated_channels.append(channel_username)

        
        
    for channel_username in channel_usernames:
        if channel_username not in updated_channels:
            delete_file(f'data/json_messages/{channel_username}.json')
    for channel_username in channel_usernames:
        if channel_username not in updated_channels:
            delete_folder(f'data/messages/{channel_username}')
        
    with open('data/last_message_ids.json', 'w', encoding='utf-8') as f:
        json.dump(last_message_ids, f, ensure_ascii=False, indent=4)