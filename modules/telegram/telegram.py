import json
import os

from dotenv import load_dotenv
from telethon.sync import TelegramClient
from ..utils import delete_folder
from ..const import NEW_CHANNEL_LAST_MESSAGES_AMOUNT, SPLIT_LENGTH_FOR_PROMPT, KEY_WORDS, DATABASE
from .db import write_new_messages_to_db, get_last_message_ids, update_last_message_ids, get_messages_by_date_and_channel

load_dotenv()
api_id = os.getenv('TELEGRAM_API_ID')
api_hash = os.getenv('TELEGRAM_API_HASH')
phone_number = os.getenv('TELEGRAM_PHONE_NUMBER')
with open('projects.json', 'r') as f:
    projects = json.load(f)
client = TelegramClient('telegram', api_id, api_hash)

async def start_telegram():
    await client.start(phone_number)

async def get_all_new_messages(last_message_ids):
    all_new_messages = []
    for project in projects:
        for channel in project['telegram_channels']:
            try:
                channel_entity = await client.get_entity(channel)
            except ValueError as e:
                print(f'{e}. Channel does not exist.')
                continue
            new_messages_of_channel = {
                'channel': channel,
                'project': project['project'],
                'messages': []
            }
            min_id = int(last_message_ids.get(channel, 0))
            limit = None if min_id else NEW_CHANNEL_LAST_MESSAGES_AMOUNT
            isFirst = True
            async for message in client.iter_messages(channel_entity, min_id=min_id, limit=limit):
                if isFirst:
                    last_message_ids[channel] = message.id
                    isFirst = False
                new_messages_of_channel['messages'].insert(0, {
                    'date': message.date.isoformat(),
                    'message': message.text,
                })
            if new_messages_of_channel['messages']:
                all_new_messages.append(new_messages_of_channel)
    return all_new_messages
  
def save_messages_to_json(all_new_messages):
    updated_channels=[]
    delete_folder(f'data/json_messages')
    if not os.path.exists(f'data/json_messages'):
        os.makedirs(f'data/json_messages')
    for new_messages_of_channel in all_new_messages:
        channel = new_messages_of_channel['channel']
        project_name = new_messages_of_channel['project']
        with open(f'data/json_messages/{channel}({project_name}).json', 'w', encoding='utf-8') as f:
            json.dump(new_messages_of_channel, f, ensure_ascii=False, indent=4)
        updated_channels.append(channel)

async def save_telegram_messages():
    if not os.path.exists(f'data'):
        os.makedirs(f'data')
    last_message_ids = get_last_message_ids()
    all_new_messages = await get_all_new_messages(last_message_ids)
    write_new_messages_to_db(all_new_messages)
    update_last_message_ids(last_message_ids)