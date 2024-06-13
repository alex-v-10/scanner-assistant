import asyncio
import traceback

from modules.db import create_table
from modules.telegram.telegram import save_telegram_messages, start_telegram, process_messages_with_chatbot, filter_chatbot_answers
from modules.browser.browser import browse
from modules.telegram.db import clean_chatbot_answers, clean_answer_search


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

# def main_async():
#     create_table()
#     loop = asyncio.get_event_loop()

#     try:
#         loop.run_until_complete(main_async())
#     except KeyboardInterrupt:
#         print("\nProgram interrupted. Exiting...")
#         loop.run_until_complete(shutdown(loop))
#     except Exception as e:
#         traceback.print_exc() 
#         print(f"An unexpected error occurred: {e}")
#         loop.run_until_complete(shutdown(loop))
#     finally:
#         loop.close()

async def main_async():
    # await start_telegram()
    while True:
        print("")
        print("Press 1 to save new Telegram messages to the database.")
        print("Press 2 to process Telegram messages with chatbot.")
        print("Press 3 Search in Telegram chatbot answers")
        print("Press 4 to test the browser.")
        print("Press 5 to exit the program.") 
        choice = input("Enter your choice: ")
        if choice == '1':
            try:
                print("Saving new telegram messages to the database...")
                await save_telegram_messages()
                print("Messages saved successfully.")
            except Exception as e:
                traceback.print_exc() 
                print(f"An error occurred: {e}")
        elif choice == '2':
            date_channel = input("Input YYYY-MM-DD or YYYY-MM-DD @channel_name: ")
            process_messages_with_chatbot(date_channel)
            # clean_chatbot_answers()
        elif choice == '3':
            date = input("Input YYYY-MM-DD: ")
            filter_chatbot_answers(date)
            print('Search finished.')
            # clean_answer_search()
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
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\nProgram interrupted. Exiting...")
    except Exception as e:
        traceback.print_exc()
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    main()