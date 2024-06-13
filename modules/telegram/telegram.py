import json
import os
import traceback

from dotenv import load_dotenv
from telethon.sync import TelegramClient

from ..chatbot.chatbot import complete_complex_chat
from ..const import (KEY_WORDS, MAX_MESSAGES_FOR_CHATBOT,
                     NEW_CHANNEL_LAST_MESSAGES_AMOUNT, SPLIT_LENGTH_FOR_PROMPT)
from ..utils import delete_folder, split_prompt
from .db import (get_chatbot_answers_by_date, get_last_message_ids,
                 get_messages_by_date_and_channel, update_chatbot_answers,
                 update_answer_search, update_last_message_ids,
                 write_new_messages_to_db)

load_dotenv()
api_id = os.getenv('TELEGRAM_API_ID')
api_hash = os.getenv('TELEGRAM_API_HASH')
phone_number = os.getenv('TELEGRAM_PHONE_NUMBER')
with open('projects.json', 'r') as f:
    projects = json.load(f)

# client = TelegramClient('telegram', api_id, api_hash)

async def start_telegram():
    client = TelegramClient('telegram', api_id, api_hash)
    await client.start(phone_number)
    return client

async def get_all_new_messages(last_message_ids):
    client = await start_telegram()
    all_new_messages = []
    try:
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
                    print(f'{channel} messages added')
    except Exception as e:
        traceback.print_exc() 
        print(f"An unexpected error occurred: {e}")
    finally:
        await client.disconnect()
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
    save_messages_to_json(all_new_messages)
    
def process_messages_with_chatbot(date_channel):
    date_channel_parts = date_channel.split(' ', 1)
    date = date_channel_parts[0]
    Input_channel = ''
    if len(date_channel_parts) > 1:
        Input_channel = date_channel_parts[1]
    
    messages_by_date = get_messages_by_date_and_channel(date, Input_channel)
    if not messages_by_date:
        print('No messages found.')
        return
    for messages_of_channel in messages_by_date:
        for message in messages_of_channel['messages']:
            del message['date']
    update_chatbot_answers(messages_by_date, date)
            
def filter_chatbot_answers(date):
    answers_by_date = get_chatbot_answers_by_date(date)
    if not answers_by_date:
        print('No chatbot answers found.')
        return
    update_answer_search(date, answers_by_date, KEY_WORDS)
            