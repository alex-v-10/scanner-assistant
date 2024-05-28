import asyncio

from modules.telegram import save_telegram_messages


def main():
    asyncio.run(save_telegram_messages())

if __name__ == '__main__':
    main()