import json
import os

from dotenv import load_dotenv
from telethon.sync import TelegramClient
from .utils import delete_file

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
                difference = 10
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
                      'date': message.date.isoformat(),
                      'message_id': message.id,
                      'text': message.text
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
        with open(f'data/messages/{channel_username}.json', 'w', encoding='utf-8') as f:
            json.dump(message_data, f, ensure_ascii=False, indent=4)
        updated_channels.append(channel_username)
        
    for channel_username in channel_usernames:
        if channel_username not in updated_channels:
            delete_file(f'data/messages/{channel_username}.json')
        
    with open('data/last_message_ids.json', 'w', encoding='utf-8') as f:
        json.dump(last_message_ids, f, ensure_ascii=False, indent=4)