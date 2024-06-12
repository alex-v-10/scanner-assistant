import os
import json
import traceback

from groq import Groq
from dotenv import load_dotenv
from ..telegram.db import get_messages_by_date_and_channel
from ..utils import split_prompt
from ..const import SPLIT_LENGTH_FOR_PROMPT, MAX_MESSAGES_FOR_CHATBOT
from .db import update_chatbot_answer

load_dotenv()

client = Groq(
    api_key=os.getenv('GROQ_API_KEY'),
)

description = 'This is chat of a crypto project.'

questions = [
  'What is the date of the conversation?',
  'Are there releases, launches or listings planned? If yes what is the date?',
  'What events are happening or planned to happen soon? If yes what is the date?',
]

def complete_complex_chat(splitted_data):
    answers = []
    count = 1
    for part in splitted_data:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"{part}",
                }
            ],
            model="llama3-8b-8192",
        )
        answers.append(f'CHATBOT ANSWER PART {count}:\n\n'+ chat_completion.choices[0].message.content)
        count += 1
    return answers
    
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
        channel = messages_of_channel['channel']
        if len(messages_of_channel['messages']) > MAX_MESSAGES_FOR_CHATBOT:
            print(f'{date} {channel} ignored. Too many messages: >{MAX_MESSAGES_FOR_CHATBOT}.')
            continue
        try:
            splitted_data = split_prompt(json.dumps(messages_of_channel), SPLIT_LENGTH_FOR_PROMPT, description, questions)
            answers = complete_complex_chat(splitted_data)
            answers_str = '\n\n'.join(answers)
            update_chatbot_answer(answers_str, date, channel)
            print(f'{date} {channel} completed')
        except Exception as e:
            traceback.print_exc() 
            print(f"An unexpected error occurred: {e}")
            print(f'{date} {channel} is not completed')

        
    