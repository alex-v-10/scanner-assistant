import asyncio
import traceback
import json

from modules.browser.browser import browse
from modules.db import create_table
from modules.telegram.telegram import (process_messages_with_chatbot,
                                       save_telegram_messages,
                                       search_in_answers, search_in_messages)
from modules.telegram.utils import clean_chatbot_answers, clean_search
from modules.charts.charts import update_charts

with open('projects.json', 'r') as f:
    projects = json.load(f)

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
        print("Press 4 to update charts.")
        print("Press x to exit the program.") 
        choice = input("Enter your choice: ")
        if choice == '1':
            await save_telegram_messages(projects)
        elif choice == '2':
            date_channel = input("Input YYYY-MM-DD or YYYY-MM-DD @channel_name: ")
            process_messages_with_chatbot(date_channel, projects)
            # clean_chatbot_answers()
        elif choice == '3':
            date = input("Input YYYY-MM-DD: ")
            search_in_answers(date, projects)
            search_in_messages(date, projects)
            print('Search finished.')
            # clean_search()
        elif choice == '4':
            number = input('Choose number of days from today to update charts (1 - 7): ')
            try:
                number = int(number)  # Convert input to integer
                if 1 <= number <= 7:
                    update_charts(number, projects)
                    print('Updated.')
                else:
                    print("Input is outside the range of 1 to 7.")
            except ValueError:
                print("Invalid input. Please enter a valid integer.")
        elif choice == 'x':
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