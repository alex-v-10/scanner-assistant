import json
import os
import traceback
import sqlite3

from dotenv import load_dotenv
from telethon.sync import TelegramClient

from ..const import (KEY_WORDS, DATABASE)
from ..utils import delete_folder, search_keyword_in_text
from .get import get_new_telegram_messages, get_messages_db, get_chatbot_answer_db, get_chatbot_answer, get_telegram_min_id
from .set import set_new_telegram_messages, set_chatbot_answer, set_answer_search, set_messages_search
from .utils import save_messages_to_json
from ..chatbot.chatbot import get_groq_client

load_dotenv()
api_id = os.getenv('TELEGRAM_API_ID')
api_hash = os.getenv('TELEGRAM_API_HASH')
phone_number = os.getenv('TELEGRAM_PHONE_NUMBER')
with open('projects_test.json', 'r') as f:
    projects = json.load(f)
with open('ignore.json', 'r') as f:
    ignore_list = json.load(f)

async def start_telegram():
    client = TelegramClient('telegram', api_id, api_hash)
    await client.start(phone_number)
    return client

async def save_telegram_messages():
    telegram_client = await start_telegram()
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        for project in projects:
            for channel in project['telegram_channels']:
                try:
                    channel_entity = await telegram_client.get_entity(channel)
                    async for message in telegram_client.iter_messages(channel_entity, limit=1):
                        newest_message_id = message.id
                    while True:
                        min_id = int(get_telegram_min_id(channel, cursor))
                        if min_id < newest_message_id:
                            new_messages = await get_new_telegram_messages(channel, project, channel_entity, min_id, telegram_client, cursor)
                            if new_messages:
                                set_new_telegram_messages(channel, project['project'], new_messages, cursor)
                                conn.commit()
                                print(f'{channel} batch of messages saved.')
                            else:
                                break
                        else:
                            break
                except Exception as e:
                    traceback.print_exc() 
                    print(f"An unexpected error occurred: {e}")
                    print(f"Unable to download and save messages from {channel}.")
    except Exception as e:
        traceback.print_exc() 
        print(f"An unexpected error occurred: {e}")
    finally:
        cursor.close()
        conn.close()
        try:
            await telegram_client.disconnect()
        except Exception as e:
            traceback.print_exc() 
            print(f"An unexpected error occurred: {e}")

def process_channel_messages_with_chatbot(date, channel, conn, cursor, groq_client):
    try:
        messages = get_messages_db(date, channel, cursor)
        if messages:
            answer = get_chatbot_answer(date, channel, messages, groq_client)
            set_chatbot_answer(date, channel, answer, conn, cursor)
    except Exception as e:
        traceback.print_exc() 
        print(f"An unexpected error occurred: {e}")
        print(f"Unable to get chatbot answer for {channel}.")

def process_messages_with_chatbot(date_channel):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    groq_client = get_groq_client()
    
    date_channel_parts = date_channel.split(' ', 1)
    date = date_channel_parts[0]
    input_channel = None
    if len(date_channel_parts) > 1:
        input_channel = date_channel_parts[1]
    try:
        if input_channel:
            process_channel_messages_with_chatbot(date, input_channel, conn, cursor, groq_client)
        else:
            for project in projects:
                for channel in project['telegram_channels']:
                    if channel in ignore_list:
                        print(f'{channel} in ignore list.')
                        continue
                    process_channel_messages_with_chatbot(date, channel, conn, cursor, groq_client)
    except Exception as e:
        traceback.print_exc() 
        print(f"An unexpected error occurred: {e}")
    finally:
        cursor.close()
        conn.close()
        groq_client.close()

def search_in_answers(date):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        for project in projects:
            for channel in project['telegram_channels']:
                answer = get_chatbot_answer_db(date, channel, cursor)
                if answer:
                    answer_lower = answer.lower()
                    search_results = []
                    for keyword in KEY_WORDS['upper']:
                        if keyword in answer:
                            result = search_keyword_in_text(answer, keyword)
                            search_results.append(result)
                    for keyword in KEY_WORDS['lower']:
                        if keyword in answer_lower:
                            result = search_keyword_in_text(answer_lower, keyword)
                            search_results.append(result)
                    if search_results:
                        set_answer_search(date, channel, search_results, cursor)
        conn.commit()
    except Exception as e:
        traceback.print_exc() 
        print(f"An unexpected error occurred: {e}")
    finally:
        cursor.close()
        conn.close()

def search_in_messages(date):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    try:
        for project in projects:
            for channel in project['telegram_channels']:
                messages = get_messages_db(date, channel, cursor)
                if messages:
                    found_messages = []
                    for message in messages:
                        if message['message'] is None:
                            continue
                        for word in KEY_WORDS['lower']:
                            if word in message['message'].lower():
                                found_messages.append(message)
                                break
                    if found_messages:
                        set_messages_search(date, channel, found_messages, cursor)
        conn.commit()
    except Exception as e:
        traceback.print_exc() 
        print(f"An unexpected error occurred: {e}")
    finally:
        cursor.close()
        conn.close()