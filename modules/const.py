# DATABASE = 'data.db'
DATABASE = 'test.db'
NEW_CHANNEL_LAST_MESSAGES_AMOUNT = 100
NEW_CHANNEL_LAST_MESSAGES_AMOUNT_SMALL = 5
MESSAGES_BATCH_LIMIT = 1000
SPLIT_LENGTH_FOR_PROMPT = 18000
MAX_MESSAGES_FOR_CHATBOT = 500
MAX_PARTS_FOR_CHATBOT = 10
KEY_WORDS = {
    'upper': [
        'May'
    ],
    'lower': [
        'january', 'february', 'march', 'april', 'june',
        'july', 'august', 'september', 'october', 'november', 'december'
    ],
}
CHATBOT = {
    'chatbot_description': 'This is chat of a crypto project.',
    'chatbot_questions': [
        'Are there releases, launches or listings planned? If yes what is the date?',
        'What events are happening or planned to happen soon? If yes what is the date?',
        'Are there any new features planned?',
    ]
}
