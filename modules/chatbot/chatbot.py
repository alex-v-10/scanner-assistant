import os

from groq import Groq

def get_groq_client():
    client = Groq(
        api_key=os.getenv('GROQ_API_KEY'),
    )
    return client

def complete_complex_chat(splitted_data, client):
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
       
    