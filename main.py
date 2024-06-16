import asyncio
import traceback

from modules.browser.browser import browse
from modules.db import create_table
from modules.telegram.telegram import (process_messages_with_chatbot,
                                       save_telegram_messages,
                                       search_in_answers, search_in_messages)
from modules.telegram.utils import clean_chatbot_answers, clean_search


async def shutdown(loop, signal=None):
    """Cleanup tasks tied to the service's shutdown."""
    if signal:
        print(f"Received exit signal {signal.name}...") 
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    print(f"Cancelling {len(tasks)} outstanding tasks")
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()

async def main_async():
    while True:
        print("")
        print("Press 1 to save new Telegram messages to the database.")
        print("Press 2 to process Telegram messages with chatbot.")
        print("Press 3 to search keywords in Telegram messages and chatbot answers")
        print("Press 4 to test the browser.")
        print("Press 5 to exit the program.") 
        choice = input("Enter your choice: ")
        if choice == '1':
            await save_telegram_messages()
        elif choice == '2':
            date_channel = input("Input YYYY-MM-DD or YYYY-MM-DD @channel_name: ")
            process_messages_with_chatbot(date_channel)
            # clean_chatbot_answers()
        elif choice == '3':
            date = input("Input YYYY-MM-DD: ")
            search_in_answers(date)
            search_in_messages(date)
            print('Search finished.')
            # clean_search()
        elif choice == '4':
            print("Open browser")
            browse()
            print("Close browser")
        elif choice == '5':
            print("Exiting the program.")
            await shutdown(asyncio.get_running_loop())
            break
        else:
            print("Invalid choice. Please try again.")
        
def main():
    create_table()
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\nProgram interrupted. Exiting...")
    except Exception as e:
        traceback.print_exc()
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    main()