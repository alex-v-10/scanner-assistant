import asyncio
import sys

from modules.db import create_table
from modules.telegram.telegram import save_telegram_messages, start_telegram
from modules.browser.browser import browse


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

def main():
    create_table()
    loop = asyncio.get_event_loop()
    async def main_async():
        await start_telegram()
        while True:
            print("")
            print("Press 1 to save new Telegram messages to the database.")
            print("Press 2 to test the browser.")
            print("Press 3 to exit the program.")       
            choice = input("Enter your choice: ")
            if choice == '1':
                try:
                    print("Saving new telegram messages to the database...")
                    await save_telegram_messages()
                    print("Messages saved successfully.")
                except Exception as e:
                    print(f"An error occurred: {e}")
            elif choice == '2':
                print("Open browser")
                browse()
                print("Close browser")
            elif choice == '3':
                print("Exiting the program.")
                await shutdown(loop)
                break
            else:
                print("Invalid choice. Please try again.")
    try:
        loop.run_until_complete(main_async())
    except KeyboardInterrupt:
        print("\nProgram interrupted. Exiting...")
        loop.run_until_complete(shutdown(loop))
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        loop.run_until_complete(shutdown(loop))
    finally:
        loop.close()

if __name__ == '__main__':
    main()