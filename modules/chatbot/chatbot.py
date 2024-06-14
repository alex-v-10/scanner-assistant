import os
import json
import traceback

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def get_groq_client():
    client = Groq(
        api_key=os.getenv('GROQ_API_KEY'),
    )
    return client

def complete_complex_chat(splitted_data, client):
    answers = []
    count = 1
    try:
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
    except Exception as e:
        traceback.print_exc() 
        print(f"An unexpected error occurred: {e}")
    return answers
       
    