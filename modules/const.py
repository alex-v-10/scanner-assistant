DATABASE = 'data.db'
# DATABASE = 'data_2.db'
# DATABASE = 'test.db'
NEW_CHANNEL_LIMIT = 5
NEW_CHANNEL_LIMIT_SMALL = 5
MESSAGES_BATCH_LIMIT = 1000
SPLIT_LENGTH_FOR_PROMPT = 18000
MAX_MESSAGES_FOR_CHATBOT = 500
MAX_PARTS_FOR_CHATBOT = 10
KEY_WORDS = {
    'upper': [
        'May'
    ],
    '1': [
        'january', 'february', 'march', 'april', 'june',
        'july', 'august', 'september', 'october', 'november', 'december', 'tomorrow',
        'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'
    ],
    '2': [
        'release', 'launch', 'alpha', 'beta', 'list', 'drop', 'snapshot'
    ],
}
CHATBOT = {
    'chatbot_description': 'This is chat of a crypto project.',
    'chatbot_questions': [
        'Are there any releases, launches or listings planned? If yes, what date?',
        'What events are happening or planned in the near future? If yes, what date?',
        'Are there any new features planned?'
    ]
}
