from telethon.sync import TelegramClient
from dotenv import load_dotenv
import os
import json
import asyncio

load_dotenv()

api_id = os.getenv('TELEGRAM_API_ID')
api_hash = os.getenv('TELEGRAM_API_HASH')
phone_number = os.getenv('TELEGRAM_PHONE_NUMBER')
channel_usernames = os.getenv('TELEGRAM_CHANNEL_USERNAMES').split(',')

loop_count = 0

client = TelegramClient('session_name', api_id, api_hash)

async def get_unread_counts(last_message_ids):
    unread_counts = {}
    for channel_username in channel_usernames:
        channel = await client.get_entity(channel_username)
        async for message in client.iter_messages(channel, limit=1):
            message_id = message.id
            last_message_id = last_message_ids.get(channel_username, message_id)
            difference = message_id - last_message_id
            unread_counts[channel_username] = difference
            last_message_ids[channel_username] = message_id
    return unread_counts
  
async def get_new_messages(unread_counts):
    new_messages = []
    for channel_username in channel_usernames:
          if unread_counts[channel_username] > 0:
              channel = await client.get_entity(channel_username)
              async for message in client.iter_messages(channel, limit=unread_counts[channel_username]):
                  message_data = {
                      'channel': channel_username,
                      'date': message.date.isoformat(),
                      'message_id': message.id,
                      'text': message.text
                  }
                  new_messages.append(message_data)
    return new_messages

async def fetch_messages():
    await client.start(phone_number)
    
    last_message_ids = {}
    if os.path.exists('data/last_message_ids.json'):
        with open('data/last_message_ids.json', 'r', encoding='utf-8') as f:
            last_message_ids = json.load(f)
    
    unread_counts = await get_unread_counts(last_message_ids)
    new_messages = await get_new_messages(unread_counts)
            
    with open('data/new_messages.json', 'w', encoding='utf-8') as f:
        json.dump(new_messages, f, ensure_ascii=False, indent=4)
        
    with open('data/last_message_ids.json', 'w', encoding='utf-8') as f:
        json.dump(last_message_ids, f, ensure_ascii=False, indent=4)
        
    global loop_count
    loop_count = loop_count + 1
    print(loop_count)
    
async def run_periodically(interval):
    while True:
        await fetch_messages()
        await asyncio.sleep(interval)
        
def main():
    interval = 30
    asyncio.run(run_periodically(interval))   

if __name__ == '__main__':
    main()