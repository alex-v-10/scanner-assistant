import json
import os

from dotenv import load_dotenv
from telethon.sync import TelegramClient
from .utils import split_prompt, delete_folder, delete_file
from .const import NEW_CHANNEL_LAST_MESSAGES_AMOUNT, SPLIT_LENGTH_FOR_PROMPT, KEY_WORDS
from modules.database import write_new_messages_to_db, write_db_to_dict

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
                difference = NEW_CHANNEL_LAST_MESSAGES_AMOUNT
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
                  new_messages_of_channel['messages'].insert(0, {
                      'date': message.date.isoformat(),
                      'content': message.text,
                  })
              all_new_messages.append(new_messages_of_channel)
    return all_new_messages
  
def get_all_splitted_messages(all_new_messages):
    all_splitted_messages = []
    for new_messages_of_channel in all_new_messages:
        channel_name = new_messages_of_channel['channel']
        splitted_data = split_prompt(json.dumps(new_messages_of_channel), SPLIT_LENGTH_FOR_PROMPT)
        all_splitted_messages.append({
            'channel': channel_name,
            'messages': splitted_data
        })
    return all_splitted_messages
  
def get_new_important_messages(all_new_messages):
    new_important_messages = []
    for new_messages_of_channel in all_new_messages:
        channel_name = new_messages_of_channel['channel']
        new_important_messages_of_channel = {
            'channel': channel_name,
            'messages': []
        }
        for message in new_messages_of_channel['messages']:
            if message['content'] is None:
                continue
            for word in KEY_WORDS['priority1']:
                if word in message['content'].lower():
                    new_important_messages_of_channel['messages'].append(message)
                    break
        if new_important_messages_of_channel['messages']:
            new_important_messages.append(new_important_messages_of_channel)
    return new_important_messages
  
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
            
      
def save_splitted_messages(all_splitted_messages):
    updated_channels=[]
    for splitted_messages_of_channel in all_splitted_messages:
        channel_name = splitted_messages_of_channel['channel']

        if not os.path.exists(f'data/splitted_messages'):
            os.makedirs(f'data/splitted_messages')

        if not os.path.exists(f'data/splitted_messages/{channel_name}'):
            os.makedirs(f'data/splitted_messages/{channel_name}')
        
        for messages_item in splitted_messages_of_channel['messages']:
            with open(f'data/splitted_messages/{channel_name}/{messages_item['name']}.txt', 'w', encoding='utf-8') as f:
                f.write(messages_item['content'])
        updated_channels.append(channel_name)
        
    for channel_name in channel_names:
        if channel_name not in updated_channels:
            delete_folder(f'data/splitted_messages/{channel_name}')

async def save_telegram_messages():
    await client.start(phone_number)
    
    if not os.path.exists(f'data'):
        os.makedirs(f'data')
    
    if os.path.exists('data/last_message_ids.json'):
        with open('data/last_message_ids.json', 'r', encoding='utf-8') as f:
            last_message_ids = json.load(f)
    else:
        last_message_ids = {}
    
    all_new_messages = await get_all_new_messages(last_message_ids)
    
    # delete_file('info.db')
    write_new_messages_to_db(all_new_messages)
    # all_splitted_messages = get_all_splitted_messages(all_new_messages) 
    
    save_messages_to_json(all_new_messages)
    # save_splitted_messages(all_splitted_messages)
    
    # new_important_messages = get_new_important_messages(all_new_messages)
    # save_messages_to_json(new_important_messages)
        
    with open('data/last_message_ids.json', 'w', encoding='utf-8') as f:
        json.dump(last_message_ids, f, ensure_ascii=False, indent=4)