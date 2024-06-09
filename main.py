import asyncio

from modules.database import create_table
from modules.telegram import save_telegram_messages


def main():
    create_table()
    asyncio.run(save_telegram_messages())

if __name__ == '__main__':
    main()