import json

from ..chatbot.chatbot import complete_complex_chat
from ..const import (CHATBOT, MAX_PARTS_FOR_CHATBOT,
                     NEW_CHANNEL_LAST_MESSAGES_AMOUNT,
                     NEW_CHANNEL_LAST_MESSAGES_AMOUNT_SMALL,
                     SPLIT_LENGTH_FOR_PROMPT)
from ..utils import split_prompt
from .set import set_last_message_id

small_channels = ["@sophiaverseann", "@PriceSoph"]

def get_last_message_id(channel, cursor):
    cursor.execute('SELECT last_id FROM telegram_last_ids WHERE channel = ?', (channel,))
    row = cursor.fetchone()
    if row:
        return row[0]
    else:
        return 0
      
async def get_new_telegram_messages(channel, telegram_client, cursor):
    channel_entity = await telegram_client.get_entity(channel)
    new_messages = []
    if channel in small_channels:
        new_channel_limit = NEW_CHANNEL_LAST_MESSAGES_AMOUNT_SMALL
    else:
        new_channel_limit = NEW_CHANNEL_LAST_MESSAGES_AMOUNT
    min_id = int(get_last_message_id(channel, cursor))
    limit = None if min_id else new_channel_limit
    isFirst = True
    async for message in telegram_client.iter_messages(channel_entity, min_id=min_id, limit=limit):
        if isFirst:
            last_message_id = message.id
            set_last_message_id(channel, last_message_id, cursor)
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