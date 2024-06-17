import json

from ..chatbot.chatbot import complete_complex_chat
from ..const import (CHATBOT, MAX_PARTS_FOR_CHATBOT,
                     NEW_CHANNEL_LAST_MESSAGES_AMOUNT,
                     NEW_CHANNEL_LAST_MESSAGES_AMOUNT_SMALL,
                     SPLIT_LENGTH_FOR_PROMPT, MESSAGES_BATCH_LIMIT)
from ..utils import split_prompt
from .set import set_telegram_min_id

def get_telegram_min_id(channel, cursor):
    cursor.execute('SELECT min_id FROM telegram_min_ids WHERE channel = ?', (channel,))
    row = cursor.fetchone()
    if row:
        return row[0]
    else:
        return 0

async def get_new_telegram_messages(channel, project, channel_entity, min_id, telegram_client, cursor):
    new_messages = []
    if min_id:
        limit = MESSAGES_BATCH_LIMIT
        async for message in telegram_client.iter_messages(channel_entity, min_id=min_id, limit=limit, reverse=True):
            min_id = message.id
            new_messages.append({
                'id': message.id,
                'date': message.date.isoformat(),
                'message': message.text,
            })
        set_telegram_min_id(channel, min_id, cursor)
    else:
        small_channels = project.get('small_telegram_channels', [])
        if channel in small_channels:
            limit = NEW_CHANNEL_LAST_MESSAGES_AMOUNT_SMALL
        else:
            limit = NEW_CHANNEL_LAST_MESSAGES_AMOUNT
        isFirst = True
        async for message in telegram_client.iter_messages(channel_entity, min_id=min_id, limit=limit):
            if isFirst:
                min_id = message.id
                set_telegram_min_id(channel, min_id, cursor)
                isFirst = False
            new_messages.insert(0, {
                'id': message.id,
                'date': message.date.isoformat(),
                'message': message.text,
            })
    return new_messages

  
def get_messages_db(date, channel, cursor):
    cursor.execute('''
            SELECT messages
            FROM telegram_messages
            WHERE date=? AND channel=?
        ''', (date, channel))
    row = cursor.fetchone()
    if row:
        return json.loads(row[0])
    else:
        return None
      
def get_chatbot_answer(date, channel, messages, groq_client):
    for message in messages:
        message.pop('id', None)
        message.pop('date', None)
    prepared_data = {
      'channel': channel,
      'messages': messages
    }
    splitted_data = split_prompt(
      json.dumps(prepared_data),
      SPLIT_LENGTH_FOR_PROMPT,
      CHATBOT['chatbot_description'],
      CHATBOT['chatbot_questions']
    )
    splitted_length = len(splitted_data)
    if splitted_length > MAX_PARTS_FOR_CHATBOT:
        print(f'{date} {channel} ignored. Too many data. {splitted_length} parts.')
        return
    answers = complete_complex_chat(splitted_data, groq_client)
    answers_str = '\n\n'.join(answers)
    return answers_str
  
def get_chatbot_answer_db(date, channel, cursor):
  cursor.execute('''
      SELECT chatbot_answer 
      FROM telegram_messages
      WHERE date=? AND channel=?
  ''', (date, channel))
  row = cursor.fetchone()
  if row:
      return row[0]
  else:
      return None