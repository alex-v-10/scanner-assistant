import os
import json

from groq import Groq
from dotenv import load_dotenv
from ..telegram.db import get_messages_by_date
from ..telegram.telegram import get_all_splitted_messages
from ..utils import find_dict_by_key_value, split_prompt
from ..const import SPLIT_LENGTH_FOR_PROMPT

load_dotenv()

client = Groq(
    api_key=os.getenv('GROQ_API_KEY'),
)

channels_to_ignore = ['@gateio_en', '@ASI_Alliance']

questions = [
  'This is chat of a crypto project.',
  'What is the date of the conversation?',
  'Are there releases, launches or listings planned? If yes what is the date?',
  'What events are happening or planned to happen soon? If yes what is the date?',
]

def complete_complex_chat(splitted_data):
    answers = []
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
        answers.append(chat_completion.choices[0].message.content)
    return answers
    
def process_messages_by_chatbot(date='2024-06-12'):
    messages_by_date = get_messages_by_date(date)
    for messages_of_channel in messages_by_date:
        channel = messages_of_channel['channel']
        splitted_data = split_prompt(json.dumps(messages_of_channel), SPLIT_LENGTH_FOR_PROMPT, questions)
        answers = complete_complex_chat(splitted_data)
    